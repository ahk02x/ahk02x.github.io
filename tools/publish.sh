#!/bin/zsh
# Publish ahk02x.dev's live data: recount Claude/GPT tokens and GitHub activity, refresh the SQ5
# trends and the weekly health card, rebuild every page, run the site tests, push to main.
#
# Runs daily from launchd (com.ahk02x.site-publish) and on demand as `site-publish`.
#
# >>> ALWAYS run the pinned runner `site-publish`, NEVER `zsh tools/publish.sh` from the worktree.
# This script resets its own worktree, which would swap this file out from under the running shell.
# Doing that on 2026-11-02 reverted the script mid-run and deleted an untracked directory in the
# owner's checkout. The guard below now refuses that, but run the pinned copy regardless.
#
# Local config, kept out of this public repo -- ~/.config/ahk02x-site/publish.env:
#   SQ_DASH_URL=    the car dashboard's drives API on the LAN
#   SQ_LOGGER=      the sq-logger checkout that renders the weekly card
#   PUBLISH_HOUR=   the hour every commit is dated
#
# Flags: --dry-run  build, test, check, show the diff, push nothing
#        --force    commit even with no change, and skip the regression gate
#
# PRIVACY, stated honestly: fixing the commit date keeps the PERMANENT git history free of
# finer-than-daily activity timing, and one push a day is the real protection. It does NOT hide
# when a push happened -- GitHub's public events feed and workflow runs expose push time to the
# second for ~90 days. Do not claim otherwise.
set -e
set -o pipefail

WT=${SITE_PUBLISH_WT:-$HOME/.local/share/ahk02x-site-publish}
PINNED=$HOME/.local/lib/ahk02x-site/publish.sh
ENVF=$HOME/.config/ahk02x-site/publish.env
LOCK=$HOME/.local/share/ahk02x-site-publish.lock
FAILED=$HOME/.local/share/ahk02x-site-publish.failed
TMP=$(mktemp -d)
trap 'rm -rf $TMP' EXIT
dry=0 force=0
for arg in "$@"; do
  case $arg in
    --dry-run) dry=1 ;;
    --force) force=1 ;;
    *) print -u2 "site-publish: unknown flag $arg"; exit 2 ;;
  esac
done
[[ -r $ENVF ]] && source $ENVF
: ${PUBLISH_HOUR:=04}
say()   { print -r -- "$(date '+%Y-%m-%d %H:%M:%S') $*" }
warn()  { say "WARN $*" }
fatal() { say "FATAL $*"; print -r -- "$(date '+%Y-%m-%d %H:%M:%S') $*" >| $FAILED; exit 1 }

# Never run from inside the tree this script resets: the reset would replace this file mid-run and
# the shell would carry on executing whatever bytes landed at the same offset.
[[ ${0:A} == $WT/* ]] \
  && fatal "refusing to run from inside the publish worktree (${0:A}) - use the pinned runner: site-publish"

# One run at a time: the scheduled run and a hand-run share one worktree, and a second run
# resetting it mid-build would stage a mix of the two.
if ! mkdir $LOCK 2>/dev/null; then
  if [[ -r $LOCK/pid ]] && kill -0 "$(<$LOCK/pid)" 2>/dev/null; then
    say "another run is active (pid $(<$LOCK/pid)); leaving it to finish"
    exit 0
  fi
  warn "breaking a stale lock from a run that died"
  rm -rf $LOCK
  mkdir $LOCK || fatal "cannot take the lock at $LOCK"
fi
print -r -- $$ >| $LOCK/pid
trap 'rm -rf $TMP $LOCK' EXIT

# The target must be THE publish worktree: a detached HEAD. The owner's own checkout has a branch
# checked out, so this refuses to reset or clean the wrong tree if SITE_PUBLISH_WT is ever wrong.
[[ -e $WT/.git ]] || fatal "no publish worktree at $WT"
[[ $(git -C $WT rev-parse --abbrev-ref HEAD 2>/dev/null) == HEAD ]] \
  || fatal "$WT has a branch checked out - refusing to touch it; the publish worktree is detached"

cd $WT
say "fetching main"
git fetch --quiet origin main
git reset --quiet --hard FETCH_HEAD
git clean -qfd

say "counting tokens"
python3 tools/tokens.py
python3 tools/gpt_tokens.py
python3 tools/gpt_history.py >/dev/null
python3 tools/github_activity.py || warn "GitHub activity refresh failed; keeping the committed numbers"

if [[ -n $SQ_DASH_URL ]]; then
  python3 tools/sq_trends.py --url $SQ_DASH_URL \
    || warn "SQ trends refresh failed; the page's own 'last updated' line goes red at 48 h"
fi
if [[ -n $SQ_LOGGER && -f $SQ_LOGGER/sq_weekly.py ]]; then
  cap=(); (( $+commands[perl] )) && cap=(perl -e 'alarm shift; exec @ARGV' 180)
  if (cd $SQ_LOGGER && $cap[@] python3 sq_weekly.py --json --pilog pi-archive/logs/power_events.log) > $TMP/weekly.json \
     && python3 -c 'import json,sys; json.load(open(sys.argv[1]))' $TMP/weekly.json; then
    python3 tools/sq_health_card.py < $TMP/weekly.json || warn "health card render failed"
  else
    warn "sq_weekly produced no usable JSON; keeping the committed health card"
  fi
fi

say "building"
python3 tools/build.py >/dev/null
say "testing"
python3 -m unittest discover -s tests >/dev/null 2>&1 || fatal "site tests failed - nothing pushed"

# Regression gate. A lifetime counter must never fall: if an archive root is missing or unreadable,
# tokens.py still writes a smaller, perfectly valid-looking total, and publishing it would quietly
# replace the real numbers with an undercount. --force overrides, for a real deletion.
if (( ! force )); then
  git show HEAD:data/tokens.json > $TMP/was.json 2>/dev/null || : > $TMP/was.json
  python3 - $TMP/was.json data/tokens.json <<'PY' \
    || fatal "token counts went BACKWARDS - refusing to publish an undercount (archive missing? use --force if the drop is real)"
import json, sys
try:
    was = json.load(open(sys.argv[1]))
except Exception:
    raise SystemExit(0)
now = json.load(open(sys.argv[2]))
for key in ('total_tokens', 'sessions', 'assistant_messages'):
    old, new = was.get(key, 0), now.get(key, 0)
    if new < old:
        print(f'{key}: {old:,} -> {new:,}', file=sys.stderr)
        raise SystemExit(1)
PY
fi

git add -A
if git diff --cached --quiet && (( ! force )); then
  say "no change to publish"
elif (( dry )); then
  say "dry run, would publish:"
  git diff --cached --stat
  git reset -q
else
  stamp="$(date '+%Y-%m-%d') ${PUBLISH_HOUR}:00:00 $(date '+%z')"
  GIT_AUTHOR_DATE=$stamp GIT_COMMITTER_DATE=$stamp \
    git commit -q --allow-empty -m "Site data: token counts, activity and the SQ5 cards"
  git push --quiet origin HEAD:main \
    || fatal "push rejected - main moved under us; nothing is lost, the next run regenerates and retries"
  say "published $(git log -1 --format=%h) to main"
fi

# Keep the pinned runner in step with the repo, but never install a script that will not parse.
# mv replaces the pathname, not the inode this run is reading, so the running copy is untouched.
if [[ -f tools/publish.sh ]] && ! cmp -s tools/publish.sh $PINNED; then
  if zsh -n tools/publish.sh 2>$TMP/syn; then
    mkdir -p ${PINNED:h}
    cp tools/publish.sh $TMP/new.sh && chmod 755 $TMP/new.sh && mv -f $TMP/new.sh $PINNED
    say "refreshed the pinned runner from the repo"
  else
    warn "repo publish.sh does not parse - keeping the working pinned runner: $(<$TMP/syn)"
  fi
fi
rm -f $FAILED
