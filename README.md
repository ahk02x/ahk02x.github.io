# ahk02x.dev

Personal site of Amir Khademi, Site Reliability Engineer, Toronto. Static HTML, served by GitHub Pages at https://ahk02x.dev.

## Publish (one run, public once it runs)

    zsh ~/Projects/ahk02x-site/publish.sh

## DNS so https://ahk02x.dev serves this site (Cloudflare, DNS-only / grey cloud)

| Type  | Name | Content                 |
|-------|------|-------------------------|
| A     | @    | 185.199.108.153         |
| A     | @    | 185.199.109.153         |
| A     | @    | 185.199.110.153         |
| A     | @    | 185.199.111.153         |
| AAAA  | @    | 2606:50c0:8000::153     |
| AAAA  | @    | 2606:50c0:8001::153     |
| AAAA  | @    | 2606:50c0:8002::153     |
| AAAA  | @    | 2606:50c0:8003::153     |
| CNAME | www  | ahk02x.github.io        |

Proxy status OFF (DNS only) so GitHub can issue the certificate. After the records exist, GitHub Pages
settings > "Enforce HTTPS" turns on by itself within an hour. Or authorize the Cloudflare connector in
Claude Code and say "dns" and the records get added from here.

## Revert

Everything is removable: `gh repo delete ahk02x/ahk02x.github.io` and `gh repo delete ahk02x/ahk02x`,
and set the profile name back blank. Search engines drop a deleted page within days.
