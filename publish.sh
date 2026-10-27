#!/bin/zsh
# Publishes the site + profile README under your name. Everything below is public once it runs.
# Run from anywhere:  zsh ~/Projects/ahk02x-site/publish.sh
set -e
SITE=~/Projects/ahk02x-site
PROF=~/Projects/ahk02x-profile

echo "== 1/4 GitHub token needs the 'user' scope once (opens a browser) =="
gh auth refresh -h github.com -s user

echo "== 2/4 site repo -> GitHub Pages (https://ahk02x.github.io, then https://ahk02x.dev) =="
cd "$SITE"
gh repo create ahk02x/ahk02x.github.io --public --source=. --remote=origin \
  --description "Personal site of Amir Khademi, SRE in Toronto. Static HTML on GitHub Pages at ahk02x.dev." --push
sleep 5
gh api -X POST repos/ahk02x/ahk02x.github.io/pages -f 'source[branch]=main' -f 'source[path]=/' >/dev/null || true
gh api -X PUT  repos/ahk02x/ahk02x.github.io/pages -f cname=ahk02x.dev -F https_enforced=false >/dev/null || true

echo "== 3/4 profile README (shows on github.com/ahk02x) =="
cd "$PROF"
gh repo create ahk02x/ahk02x --public --source=. --remote=origin \
  --description "Amir Khademi — Site Reliability Engineer, Toronto" --push

echo "== 4/4 profile name + bio + site link =="
gh api -X PATCH /user -f name='Amir Khademi' \
  -f bio='Site Reliability Engineer, Toronto. Builds monitoring, automation and agent tooling for his own infrastructure.' \
  -f blog='https://ahk02x.dev' --jq '{name,bio,blog}'

echo
echo "DONE. Live in ~1 min at https://ahk02x.github.io  (ahk02x.dev works after the DNS step in README.md)"
