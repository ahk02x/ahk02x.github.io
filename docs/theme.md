# Theme: Personal archive

The design this site now follows. Source of truth for the look; `docs/theme-reference/design-export.html`
is the original Claude Design export it was taken from (not published, kept for provenance).

## The concept

A printed personal archive, set in a single grid. One paper tone edge to edge, hairlines instead of
boxes, numbered sections like plates in a catalogue, and monospace labels for anything the machine
measured. Content sits directly on the paper: there are no cards, no shadows, no rounded corners and
no panels floating over a different background. Rules divide the page; nothing is wrapped in a frame.

Hierarchy comes from type size and the hairline, never from fills. The only saturated colour is the
rust accent and the four status hues, and they are reserved for state and data.

## Tokens

Light (default):

| token | value | use |
| --- | --- | --- |
| `--page` | `#d4d5d1` | the paper, every surface |
| `--ink` | `#1b1c1a` | text, hairline rules, fills that invert |
| `--ink-2` | `#2a2b28` | long body copy |
| `--ink-3` | `#3a3c38` | secondary copy, row descriptions |
| `--quiet` | `#555751` | mono labels, captions, meta |
| `--line` | `#1b1c1a` | structural hairline (section tops, header, tables) |
| `--line-2` | `#a9aba5` | hairline between major sections |
| `--line-3` | `#b9bbb5` | hairline between rows in a list |
| `--panel` | `#dcddd9` | the one inset surface (Now panel, chat column) |
| `--field` | `#e6e7e3` | input and form backgrounds |
| `--hover` | `#cdcec9` | row hover tint |
| `--track` | `#c6c7c2` | bar track, empty heatmap cell |
| `--img` | `#cbccc7` | image placeholder while loading |
| `--reverse` | `#e9eae6` | text on an ink fill |
| `--accent` | `oklch(0.5 0.15 45)` | rust: link hover, mono keys, the heatmap ramp |
| `--accent-hi` | `oklch(0.55 0.15 45)` | hover on the accent itself |
| `--st-live` | `oklch(0.52 0.17 25)` | live / SQ |
| `--st-run` | `oklch(0.5 0.13 150)` | running |
| `--st-built` | `oklch(0.48 0.13 255)` | built |
| `--st-written` | `oklch(0.55 0.13 70)` | written |
| `--ok-dot` | `oklch(0.6 0.15 145)` | an online indicator, the only circle |

Heatmap ramp, lightest to darkest: `--track`, `oklch(0.82 0.06 45)`, `oklch(0.72 0.11 45)`,
`oklch(0.6 0.15 45)`, `oklch(0.45 0.13 45)`.

Dark: the ink and paper swap — `--page:#121311`, `--ink:#e9eae6`, `--ink-2:#dcdcd7`, `--ink-3:#c3c4bf`,
`--quiet:#95978f`, `--line:#e9eae6`, `--line-2:#3b3d39`, `--line-3:#2c2e2a`, `--panel:#1b1c1a`,
`--field:#202121`, `--hover:#232420`, `--track:#2a2b27`, `--img:#222320`, `--reverse:#121311`. The
accent and status hues lift to `oklch(0.72 …)` so they stay legible on ink. No surface gains a border
radius or a shadow in either theme.

## Type

- `Geist` for everything that reads as language; `Geist Mono` for everything the machine produced.
  Both are self-hosted in `assets/fonts/` (variable, 400–600, latin + latin-ext) with
  `Helvetica, Arial, sans-serif` and `ui-monospace, monospace` as fallbacks.
- Headings: weight 500, **never uppercase**, `letter-spacing` −.02em at 28px tightening to −.045em at
  display sizes, `line-height` .92–1.05, `text-wrap: balance`.
  - page h1 `clamp(48px, 7.5vw, 96px)`; home h1 `clamp(56px, 9vw, 112px)`
  - section h2 `clamp(28px, 3.4vw, 42px)`; a quieter section head is a flat 28px
  - h3 / row titles 21–24px
- Body: 15px in rows and captions, 16–17px in prose, 19px in a lede paragraph, `line-height` 1.5–1.6,
  `text-wrap: pretty`, measure capped at 58–64ch.
- Eyebrows, labels, keys, dates, counts, captions: Geist Mono 11px (12px for nav and buttons),
  weight 500, `letter-spacing` .06em, uppercase, colour `--quiet`. Section eyebrows carry the plate
  number: `01 / Network`.
- Numbers that change: `font-variant-numeric: tabular-nums`, weight 500, letter-spacing −.03em.

## Layout

- One column, `max-width: 1200px`, `margin: 0 auto`, `padding: 0 clamp(16px, 4vw, 40px)`. No second
  container inside it.
- A page is a stack of full-width sections. Each ends with `border-bottom: 1px solid var(--line-2)`;
  the last one before the footer has none. Vertical rhythm: `padding: 56px 0` (`clamp(48px, 8vw, 96px)`
  above a hero, 48px on inner pages).
- Two-up sections are `display: flex; flex-wrap: wrap; gap: 32px 48px`, children `flex: 1 1 380px`, so
  they stack on their own below ~820px without a media query.
- Lists are rows, not cards: `padding: 20px 0`, `border-bottom: 1px solid var(--line-3)`, hover
  `background: var(--hover)`. A set of rows opens with `border-top: 1px solid var(--line)`.
- Grids of equal things use `repeat(auto-fit, minmax(min(100%, 340px), 1fr))` with hairlines on the
  cells, not gaps.
- Status is a 7px **square** of the status colour before a mono label. The online dot is the only
  circle on the site.
- Images: `border: 1px solid var(--ink)`, `object-fit: cover`, a stated `aspect-ratio` (4/3 in a
  section, 16/10 in a wide row), `background: var(--img)`, and a mono caption underneath in `--quiet`.
- Buttons: square, no radius. Primary is an ink fill with `--reverse` text, 14px/20px padding; secondary
  is a 1px ink outline on paper. Segmented controls are one 1px ink box holding mono 12px uppercase
  buttons; the selected one is filled ink.
- Mobile keeps the gutter at 16px and lets every two-up stack. Nothing shrinks below 11px.

## Chrome

- Header: sticky on the paper, hairline under it. Left is the wordmark `AHK / 02X` in mono 12px
  uppercase with `Personal archive` beside it in `--quiet`. Right is the numbered nav — `01 About`,
  `02 Projects`, `03 Infra`, `04 Writing`, `06 ahkira` — as mono 12px uppercase links, the current
  page filled ink, then `05 Contact ↗` as a mailto. The theme toggle sits at the end of the nav.
- Footer: hairline on top, three columns — `05 / Contact` with the address at 22px, `Directory` with
  the nav repeated, `Elsewhere` with X, LinkedIn and GitHub. All labels mono uppercase.
- Inner pages open with a two-up hero: left the plate number and `h1`, right the intro paragraph at
  `clamp(18px, 1.8vw, 21px)` in `--ink-3`. Nothing in the hero is reversed out of a dark panel.
- Inner pages close with a full-width "Next —" row linking the following section, its label at
  `clamp(28px, 4vw, 48px)`.

## Class vocabulary

Existing class names keep their meaning and are restyled in place: `.site-shell`, `.site-header`,
`.site-brand`, `.site-nav`, `.site-footer`, `.inner-page`, `.hero`, `.eyebrow`, `.lede`, `.byline`,
`.grid`, `.card`, `.items`, `.item`, `.chip`, `.glyph`, `.readouts`, `.readout`, `.tiles`, `.tile`,
`.spec`, `.bars`, `.verdict`, `.snapshot-notice`, `.sq-tabs`, `.mobile-flow`, `.hm`, `.tk-strip`,
`.muted`, `.st-live|st-run|st-built|st-written`.

New, for the sections this theme adds:

| class | what it is |
| --- | --- |
| `.band` | one full-width section with the hairline under it |
| `.band.last` | same, no hairline (sits above the footer) |
| `.band-head` | the eyebrow + h2 (+ optional right-hand control) head of a band |
| `.two-up` | the wrapping two-column flex row |
| `.now` | the inset Now panel: hairline box on `--panel`, mono header, key/value rows |
| `.feature` | the featured project: image on one side, title, copy and a three-up stat row |
| `.statrow` | three to five mono-labelled numbers under one hairline |
| `.rows` | a list of hairline rows (writing index, project list) |
| `.seg` | segmented control (one ink box, filled active button) |
| `.actgrid` | the activity heatmap block: stats strip, grid, caption |
| `.askbar` | the single-line ask form: field + ink submit button |
| `.chips` | a wrapped row of outlined mono suggestion chips |
| `.plate` | a cell in a hairline grid of equal things (the About stories) |
| `.nextnav` | the "Next —" row at the foot of an inner page |

Anything that would need a new fill, a radius, a shadow or a second background tone is wrong for this
theme: find the hairline version instead.

Also agreed, after the first pass asked for them:

| class | what it is |
| --- | --- |
| `.btn` | primary action: ink fill, `--reverse` text, square, 14px/20px padding |
| `.btn.ghost` | the same button as a 1px ink outline on paper |
| `.home` | page scope on the home `<main>`, which does **not** get `.inner-page` |

## Markup contract

The stylesheet targets this markup. It is the interface between the pages and `style.css`: a page that
needs a different shape says so here first.

- Header: `.site-header > a.site-brand` (two spans: wordmark, then `Personal archive` in `--quiet`) and
  `nav.site-nav` of `a > span.nav-no` + label, the current page carrying `aria-current="page"`, the
  mailto `05 Contact ↗` last, then `button.theme-toggle`.
- Footer: `.site-footer` with three children — a `div` whose `.eyebrow` is `05 / Contact` and whose `a`
  is the address at 22px, `nav[aria-label="Directory"]`, and `nav.social-links`. Each opens with an
  `.eyebrow`.
- Sections: `section.band`, `.band.last` for the one above the footer, `.band.two-up` when it splits.
  A head is `.band-head > div(.eyebrow + h2)` plus an optional right-hand control.
- Hero: `.band.hero.two-up` — `div(h1 + p.lede + p > a.btn)` and, on the home page, `aside.now`.
- `.now`: a `div` of two spans (label, month), a `dl` of `div(dt + dd)` rows, then a closing `p`.
- `.feature`: `figure(img + figcaption)` beside `div(div(.eyebrow + h2 + p) + .statrow + p of links)`.
- `.statrow`: direct children each `span` (mono label) + `b` (the number).
- Row lists: `.rows` wrapping the existing `.items` / `.item` markup, unchanged, so the writing index
  and the home page's latest three render identically.
- `.seg`: `role="tablist"`, `hidden` until JavaScript reveals it, holding `button[role="tab"]` with
  `aria-selected`; the active button is `[aria-selected="true"]`. The panels it switches are `.act-p`,
  hidden with the `hidden` property, never inline `display`.
- `.actgrid`: `.act-p > .act-h(h3 + span)` then `.tk-strip` (`div > b + span`), `.hm`, `.hm-m`, `.hm-k`,
  and a closing `p.muted` caption.
- `.askbar`: a real `form[method="get"][action="/ask/"]` with a labelled `input[name="q"]` and a submit
  button. It is **never** `hidden`: a GET form needs no JavaScript, and `/ask/` reads `?q=`.
- `.chips`: a wrapped set of `a` links (to `/ask/?q=…`), outlined, mono.
- `.plate`: a cell in a hairline grid; `.nextnav`: one full-width link row.

## Keep (unchanged by the restyle)

- Real numbers only. Every figure on the site comes from the build (`{{…}}` substitutions) or from a
  committed snapshot. Nothing in this theme is hard-coded, and no chart is invented to fill a space.
- Unknown telemetry never renders as healthy; a missing value stays explicitly unavailable.
- Text carries the meaning. Colour, a square, a hover or an animation is never the only signal.
- Privacy: no hostnames, employers, locations, car costs or precise timestamps.
- Every page keeps its skip link, one `<main id="main">`, its heading order and its focus outlines.
- SQ red stays for SQ state, not site chrome. The owner's Crossing mark stays his alone.
