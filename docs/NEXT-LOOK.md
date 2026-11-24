# Next: two looks, built, for him to pick

Amir's words on 2026-11-16, looking at the theme-archive branch: "everything looks ass". He approved
building variants rather than being asked to choose a direction cold. He reacts to a built thing.

## What is actually wrong, from looking at all 24 renders (both themes, every page)

1. **Every page has the same rhythm**: mono eyebrow → huge headline → hairline → rows. Home, About,
   Projects, Writing, Infra and all six SQ tabs. By the third page it reads as a template.
2. **One flat tone edge to edge.** The paper grey is every surface on every page. No white, no dark
   band, no inset. "Hairlines instead of boxes" got applied so literally that nothing has weight.
3. **Shouted headline over faint copy.** 96px display type above 15px grey body and 11px mono labels.
4. **A car project with almost no car in it.** The same photo on Home, About and Projects; the SQ
   overview has none; the gallery's 12 good pictures are used nowhere else.
5. **Dead right-hand space** at the top of SQ, About and several tabs.

## The job

Two home pages and two SQ overviews. Same content, same facts, same tokens — different structure.
Serve them side by side on localhost and let him choose. Do not ship a look he did not pick.
Both variants must still pass `tests/test_theme.py`, or the contract in `docs/theme.md` changes first
and says why.

Suggested starting points, not a decision:
- **A — range.** Keep the archive grammar, give each page one full-bleed dark band and one image-led
  section, lift body copy, and let the SQ overview open on a photograph with the readouts over it.
- **B — density.** Trade the display headlines for a tighter editorial grid: more columns, smaller
  h1, figures and numbers carrying the page instead of type size.

## Still open, from the outside review (2026-11-16)

- Two facts only he can settle: what the 3.4 W estimate was off by ten times, and what feeds the Pi
  (the pinout page implies nothing touches +12 V; the build log has it draining the battery).
- The build log still presents the September cylinder-3 coil swap as the plan; the overview says that
  test's decision rule broke.
- The health card labels "11 of 20 trips never got the oil warm" OK while giving an action.
- Copy that shrinks the work before it is read: "A peek at each", "Not the whole thing",
  "Everything else". Home also buries the one number he owns: ~40% of misfire counts in the second
  after an upshift.
- The nav still reads 01 02 03 04 06 05.
