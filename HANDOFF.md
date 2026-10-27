# ahk02x.dev — design handoff

Static site, no framework, no build server. `python3 tools/build.py` assembles `src/pages/*.html` (front matter + body) into the root with shared chrome. The live site is the `live` branch (plain, text-only). This branch is a first redesign attempt that the owner wants replaced with something better-looking.

## What to keep as-is
- All copy in `src/pages/` (it is checked for privacy; do not add car costs, locations, employers, hostnames, dates finer than a week).
- `tools/sq_health_card.py` (renders the weekly car health card from real data) and `tools/tokens.py` (counts Claude Code tokens). Their output HTML can be restyled; their numbers cannot be invented.
- `data/tokens.json` and `sq/health.json` are real.

## Brand assets (owner's own)
- `assets/mark.svg` — the ahk02x "Crossing" mark (circle with two S-curves), draw with `currentColor`. Avatar colours: carbon `#0D1013` ground, orange `#E0913F` stroke. Wordmark is monospace.
- `assets/sq-mark-dark.svg`, `assets/sq-mark-light.svg`, `assets/sq-glyph.svg` — the SQ tachometer-Q mark. SQ palette: Carbon `#0C1014`, Signal Red `#E8433C`, Graphite `#97A2AE`, Slate `#414B57`, Cool White `#F5F7F9`. Red is for signal elements only, never chrome.
- The owner's wall display is phosphor-green retro sci-fi; his taste runs to instrument panels, gauges, visual-first, high contrast. He is Deaf and reads everything, so text must carry meaning, not icons alone.

## Pages
`/` home · `/about.html` · `/projects/` (cards + token box) · `/sq/` (car build log) · `/sq/health.html` (weekly card, generated) · `/writing/` + `/writing/claude-code-on-call.html` (article) · `/404.html`.

## Must-haves
Phone width works with no horizontal scroll. Light and dark both designed. Fonts only from Google Fonts or system. No tracking scripts. Keep every number with its threshold on the car pages ("104 °C, fine, worry starts at 130").
