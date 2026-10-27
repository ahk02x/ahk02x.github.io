# ahk02x.dev — field notes

Amir Khademi's personal engineering site: the SQ5 garage, agent tooling, and notes from a home fleet. Static HTML, a shared stylesheet, and a dependency-free Python builder. No trackers or client framework.

## Run locally

Requires Python 3.12 or later.

```sh
python3 tools/build.py
python3 -m http.server 8000 --directory _site
```

Open http://localhost:8000. Rebuild after source changes. The homepage, all seven other pages, shared navigation, and theme control work from the same build.

## Edit

- `src/pages/*.html`: front matter and page content.
- `tools/build.py`: shared header/footer, substitutions, token breakdown, sitemap, public build.
- `style.css`: warm paper / carbon design, responsive layouts, light and dark themes.
- `assets/theme-init.js`, `assets/site.js`: optional theme persistence and old-snapshot notices. Navigation and content work without JavaScript.
- `tools/sq_health_card.py`: weekly health renderer. Run with the real weekly analysis JSON on stdin, then build the site.
- `tools/tokens.py`: scans the operator's local Claude transcripts; publishes only the allowlisted project names and month-granularity dates.
- `tools/public_data.py`: public token export policy. Totals stay intact; private project names never enter the export.

Do not rerun the token collector on an empty machine just to build the site: it would replace the committed usage snapshot. The build uses the committed JSON and health page.

## Check

```sh
python3 -m unittest discover -s tests -v
python3 tools/build.py
```

Tests cover empty, partial, undated, and invalid telemetry; threshold boundaries; missing comparison baselines; the public data export; page links and landmarks; and repeatable public builds. Test telemetry is synthetic and isolated in temporary directories. It never replaces the committed snapshot.

GitHub Actions runs these checks on pull requests. This workflow does not deploy.

## Review the design

Preview screenshots are in `docs/previews/`. Run the local server above for the full interactive version. The design PR targets `main`; the `live` branch is not changed by this work.

## Publication

`_site/` is the public output: pages, assets, CSS, sitemap, robots, CNAME, and sanitized JSON. It excludes source code, tests, operator scripts, handoff notes, and review screenshots. Serve it at the domain root (links start with `/`).

Root HTML remains generated and committed for the existing branch-based Pages setup. Prefer publishing `_site/` for a future artifact-based Pages workflow. There is no new deployment configuration in this redesign.

`publish.sh` and `dns.sh` are legacy initial-provisioning scripts, not preview commands. `publish.sh` creates public repositories and changes the GitHub profile; do not run it to review this PR.

The public JSON is sanitized in the current tree. Older commits retain their original contents; this PR does not rewrite repository history.
