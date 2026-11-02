#!/bin/zsh
# Publish ahk02x.dev's live data: recount Claude/GPT tokens and GitHub activity, refresh the SQ5
# trends and the weekly health card, rebuild every page, run the site tests, push to main.
#
# Runs daily from launchd (com.ahk02x.site-publish) and on demand as `site-publish`.
# Works out of its own detached worktree pinned to origin/main, so publishing does not depend on
# which branch the main checkout is on and never picks up uncommitted work sitting there.
#
# Local config, kept out of this public repo -- ~/.config/ahk02x-site/publish.env:
#   SQ_DASH_URL=    the car dashboard's drives API on the LAN
#   SQ_LOGGER=      the sq-logger checkout that renders the weekly card
#   PUBLISH_HOUR=   the hour every commit is dated; public history must not time his keyboard
#
# Flags: --dry-run  build, test, show the diff, push nothing
#        --force    commit even when nothing changed
set -e
set -o pipefail

WT=${SITE_PUBLISH_WT:-$HOME/.local/share/ahk02x-site-publish}
PINNED=$HOME/.local/lib/ahk02x-site/publish.sh
ENVF=$HOME/.config/ahk02x-site/publish.env
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
say() { print -r -- "$(date '+%Y-%m-%d %H:%M:%S') $*" }
warn() { say "WARN $*" }

[[ -e $WT/.git ]] || { say "FATAL no publish worktree at $WT"; exit 1 }
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
  if (cd $SQ_LOGGER && python3 sq_weekly.py --json --pilog pi-archive/logs/power_events.log) > $TMP/weekly.json \
     && python3 -c 'import json,sys; json.load(open(sys.argv[1]))' $TMP/weekly.json; then
    python3 tools/sq_health_card.py < $TMP/weekly.json || warn "health card render failed"
  else
    warn "sq_weekly produced no usable JSON; keeping the committed health card"
  fi
fi

say "building"
python3 tools/build.py >/dev/null
say "testing"
python3 -m unittest discover -s tests >/dev/null 2>&1 \
  || { say "FATAL site tests failed - nothing pushed"; exit 1 }

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
    git commit -qm "Site data: token counts, activity and the SQ5 cards"
  git push --quiet origin HEAD:main
  say "published $(git log -1 --format=%h) to main"
fi

# Keep the pinned runner in step with the repo. mv is atomic, so this run keeps executing its own copy.
if [[ -f tools/publish.sh ]] && ! cmp -s tools/publish.sh $PINNED; then
  mkdir -p ${PINNED:h}
  cp tools/publish.sh $TMP/publish.sh && chmod 755 $TMP/publish.sh && mv -f $TMP/publish.sh $PINNED
  say "refreshed the pinned runner from the repo"
fi
