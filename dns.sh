#!/bin/zsh
# Adds the GitHub Pages records for ahk02x.dev at Cloudflare (DNS-only). Needs a token with Zone.DNS:Edit on ahk02x.dev:
#   CLOUDFLARE_API_TOKEN=cfut_xxx zsh ~/Projects/ahk02x-site/dns.sh
set -e
: "${CLOUDFLARE_API_TOKEN:?set CLOUDFLARE_API_TOKEN}"
H=(-H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" -H "Content-Type: application/json")
ZONE=$(curl -s "${H[@]}" "https://api.cloudflare.com/client/v4/zones?name=ahk02x.dev" | python3 -c 'import sys,json;print(json.load(sys.stdin)["result"][0]["id"])')
add(){ curl -s "${H[@]}" -X POST "https://api.cloudflare.com/client/v4/zones/$ZONE/dns_records" \
  --data "{\"type\":\"$1\",\"name\":\"$2\",\"content\":\"$3\",\"proxied\":false,\"ttl\":1}" | python3 -c 'import sys,json;r=json.load(sys.stdin);print("ok" if r["success"] else r["errors"])'; }
for ip in 185.199.108.153 185.199.109.153 185.199.110.153 185.199.111.153; do add A ahk02x.dev $ip; done
for ip6 in 2606:50c0:8000::153 2606:50c0:8001::153 2606:50c0:8002::153 2606:50c0:8003::153; do add AAAA ahk02x.dev $ip6; done
add CNAME www.ahk02x.dev ahk02x.github.io
echo "records added; https://ahk02x.dev loads within a few minutes, HTTPS cert within the hour"
