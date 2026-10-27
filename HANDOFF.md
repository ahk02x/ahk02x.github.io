# ahk02x.dev — design handoff

## Current implementation

An engineering field journal: warm paper and carbon surfaces, orange accents, large condensed headlines, numbered project rows, and two distinctive homepage features for the SQ5 garage and the alert board. Dark mode follows the system until the visitor chooses a theme; the preference persists when storage is available.

`python3 tools/build.py` assembles `src/pages/*.html` into the root and creates an allowlisted `_site/` directory for preview/publication. Python 3.12+, no dependencies. Run `python3 -m unittest discover -s tests -v` for regressions. See README for preview instructions. This is a review branch; the `live` branch and deployment settings are unchanged.

## Preserve

- The owner's Crossing mark and SQ tachometer-Q brand assets.
- The evidence and lessons in the existing writing and garage pages.
- Real token totals and health measurements. Do not fabricate charts, driving data, or screenshots of systems we have not seen.
- Privacy: no car costs, new locations, employers, hostnames, or precise activity timestamps. Public token exports contain only allowlisted names and month-granularity dates. Old commits are not sanitized by changing the current tree.
- Unknown telemetry must never become a healthy verdict. Missing values stay explicitly unavailable.
- Text carries meaning. Icons, color, animation, and hover are never the only way to understand something.

## Visual system

- Carbon/orange Crossing mark; monospace wordmark.
- SQ red is reserved for SQ signals and status, not general site chrome.
- Large editorial typography and intentional whitespace; avoid a repeated grid of rounded dashboard cards.
- Light and dark both designed. System fonts are fallbacks; Google Fonts are the only external asset requests.
- Small-screen diagrams use readable step lists. Cylinder ratios have a visible table with exact values and thresholds.
- Keep thresholds next to telemetry numbers and explain that weekly reports are snapshots, not a live feed.

## Pages

Home · About · Projects + token methodology · SQ5 garage · Weekly health · Writing index + pager article · 404.
