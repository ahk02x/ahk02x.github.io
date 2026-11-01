#!/bin/zsh
# Hourly (launchd com.ahk02x.site-tokens): recount Claude + GPT tokens and rebuild the site locally.
# Pushing is OFF until ~/.config/ahk02x-site/autopush exists (create it once the redesign is live).
set -e
cd "$HOME/Projects/ahk02x-site"
python3 tools/tokens.py >/dev/null
python3 tools/gpt_tokens.py
python3 tools/github_activity.py || true
python3 tools/build.py >/dev/null
if [[ -f "$HOME/.config/ahk02x-site/autopush" && "$(git branch --show-current)" == main ]]; then
  git add data/tokens.json data/gpt_tokens.json index.html projects/index.html _site 2>/dev/null || true
  git diff --cached --quiet || { git commit -qm "Token counts $(date '+%Y-%m-%d %H:00')" && git push -q origin main; }
fi
