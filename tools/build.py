#!/usr/bin/env python3
"""Assemble the site: src/pages/*.html (front matter + body) -> root. Shared chrome, data-driven readouts, sitemap."""
import os, re, json, glob, html, datetime, shutil, collections
from public_data import public_tokens
ROOT = os.path.join(os.path.dirname(__file__), '..'); os.chdir(ROOT)
tok = public_tokens(json.load(open('data/tokens.json'))) if os.path.exists('data/tokens.json') else {}
if tok:
    with open('data/tokens.json', 'w') as public_file:
        json.dump(tok, public_file, indent=2)
        public_file.write('\n')
hc = json.load(open('sq/health.json')) if os.path.exists('sq/health.json') else {}
STATUS = {'OK': ('Healthy', 'ok'), 'WATCH': ('Keep an eye on it', 'warn'), 'FLAG': ('Needs attention', 'crit')}
word, cls = STATUS.get(hc.get('status'), ('No data', 'unknown'))
try:
    datetime.date.fromisoformat(hc.get('generated', ''))
except (TypeError, ValueError):
    word, cls = 'No dated snapshot', 'unknown'
SECTIONS = [('/about.html', 'About'), ('/projects/', 'Projects'), ('/infra.html', 'Infra'), ('/writing/', 'Writing'), ('mailto:amir@ahk02x.com', 'Contact')]
NAV = [('/', 'Home'), ('/projects/', 'Projects'), ('/infra.html', 'Infra'), ('/writing/', 'Writing'), ('/about.html', 'About')]
MARK = '<svg viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round"><circle cx="64" cy="64" r="46"/><path d="M36,82 H54 C64,82 64,46 74,46 H92"/><path d="M36,46 H54 C64,46 64,82 74,82 H92"/></g></svg>'
def glyph_svg(body, sw=10):  # one line-icon language: 128 box, round caps, currentColor so the row's status tints it
    return f'<svg class="glyph" viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>'
def dot(cx, cy, r): return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="currentColor" stroke-width="2"/>'
# One glyph per project, drawn from what the project does. The Crossing mark stays the owner's alone (MARK), never a row icon.
GLYPHS = {
 'alert': glyph_svg('<path d="M26,92 C34,84 38,72 38,56 C38,40 49,28 64,28 C79,28 90,40 90,56 C90,72 94,84 102,92 Z"/><path d="M64,28 V18"/><path d="M52,104 C54,112 74,112 76,104"/><path d="M52,60 l9,9 l17,-19"/>'),
 'phosphor': glyph_svg('<rect x="30" y="10" width="68" height="108" rx="8"/><rect x="43" y="23" width="42" height="30" rx="2" fill="currentColor" stroke-width="3"/><path d="M44,76 H84"/><path d="M44,96 H68"/>'),
 'memory': glyph_svg('<path d="M40,38 V90"/><path d="M40,76 C40,56 88,70 88,52"/><circle cx="40" cy="26" r="12"/><circle cx="40" cy="102" r="12"/><circle cx="88" cy="40" r="12"/>'),
 'patch': glyph_svg('<g transform="rotate(-45 64 64)"><rect x="8" y="40" width="112" height="48" rx="24"/><path d="M46,40 V88"/><path d="M82,40 V88"/><circle cx="64" cy="54" r="4" fill="currentColor" stroke-width="3"/><circle cx="64" cy="74" r="4" fill="currentColor" stroke-width="3"/></g>'),
 'lan': glyph_svg('<path d="M8,62 L44,28 L80,62"/><path d="M18,54 V104 H70 V54"/><path d="M50,82 H118"/><path d="M102,66 L118,82 L102,98"/>'),
 'iot': glyph_svg('<rect x="34" y="34" width="60" height="60" rx="8"/><path d="M52,14 V34 M76,14 V34 M52,94 V114 M76,94 V114 M14,52 H34 M14,76 H34 M94,52 H114 M94,76 H114"/>' + dot(64, 64, 8)),
 'coach': glyph_svg('<g transform="rotate(-40 64 64)"><path d="M36,64 H92"/><g fill="currentColor" stroke-width="6"><rect x="22" y="34" width="14" height="60" rx="4"/><rect x="92" y="34" width="14" height="60" rx="4"/><rect x="8" y="48" width="14" height="32" rx="3"/><rect x="106" y="48" width="14" height="32" rx="3"/></g></g>'),
 'flow': glyph_svg('<path d="M22,38 H106"/><path d="M22,90 H58"/>' + ''.join(dot(x, 38, 12) for x in (22, 64, 106)) + dot(22, 90, 12) + '<circle cx="106" cy="90" r="11" stroke-width="8"/>', 9),
 'mac': glyph_svg('<path d="M52,52 H76 V76 H52 Z"/><path d="M52,52 V38 A12,12 0 1 0 40,52 Z"/><path d="M76,52 V38 A12,12 0 1 1 88,52 Z"/><path d="M52,76 V90 A12,12 0 1 1 40,76 Z"/><path d="M76,76 V90 A12,12 0 1 0 88,76 Z"/>'),
 'net': glyph_svg('<rect x="14" y="26" width="100" height="76" rx="6"/><path d="M14,51 H114 M14,76 H114"/><path d="M64,26 V51 M38,51 V76 M90,51 V76 M64,76 V102"/>', 9),
 'crucix': glyph_svg('<path d="M52,16 V48 L20,100 A8,8 0 0 0 27,112 H101 A8,8 0 0 0 108,100 L76,48 V16"/><path d="M42,16 H86"/><path d="M34,86 H94"/>' + dot(60, 98, 4) + dot(78, 96, 3)),
 'inbox': glyph_svg('<path d="M18,70 L32,22 H96 L110,70 V98 A8,8 0 0 1 102,106 H26 A8,8 0 0 1 18,98 Z"/><path d="M18,70 H46 L52,86 H76 L82,70 H110"/>'),
 'code': glyph_svg('<path d="M42,34 L14,64 L42,94"/><path d="M86,34 L114,64 L86,94"/><path d="M72,24 L56,104"/>'),
 'plug': glyph_svg('<g transform="rotate(40 64 64)"><rect x="38" y="40" width="52" height="40" rx="8"/><path d="M52,40 V20 M76,40 V20"/><path d="M64,80 V112"/></g>'),
 'tokens': glyph_svg('<path d="M30,106 V82"/><path d="M64,106 V56"/><path d="M98,106 V26"/>', 17),
 'tag': glyph_svg('<path d="M22,22 H66 L106,62 L62,106 L22,66 Z"/>' + dot(44, 44, 7)),
 'sq': '<span class="sq-brand"><img class="glyph sq sq-dark" src="/assets/sq-mark-dark.svg" alt="" width="34" height="34"><img class="glyph sq sq-light" src="/assets/sq-mark-light.svg" alt="" width="34" height="34"></span>',
}
def chrome(title, desc, path, body, nav_key, extra_head=''):
    if 'Amir Khademi' not in title and title != 'Not found': title = f'{title} · Amir Khademi'  # every indexed page carries the author's name
    sec = next((h for h, _ in SECTIONS if h != 'mailto:amir@ahk02x.com' and path.startswith(h)), '')
    nav = ''.join(f'<a href="{h}"' + (' aria-current="page"' if h == sec else '') + f'><span class="nav-no" aria-hidden="true">{i:02}</span>{t}</a>' for i, (h, t) in enumerate(SECTIONS, 1))
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="https://ahk02x.dev{path}">
<link rel="icon" href="/assets/mark.svg" type="image/svg+xml">
<script src="/assets/theme-init.js"></script>
<link rel="stylesheet" href="/style.css">
<script src="/assets/site.js" defer></script>
<meta name="theme-color" content="#d4d5d1">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://ahk02x.dev{path}">
<meta property="og:image" content="https://ahk02x.dev/assets/og.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<link rel="alternate" type="application/rss+xml" title="ahk02x — field notes" href="/feed.xml">
{extra_head}</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<div class="site-shell">
<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header"><a class="site-brand" href="/">ahk02x.dev</a><nav class="site-nav" aria-label="Main navigation">{nav}</nav><button class="theme-toggle" type="button" hidden><span data-theme-label>Dark</span></button></header>
{body}
<footer class="site-footer"><span>AHK02X</span></footer>
</div>
</body>
</html>'''
def token_card():
    if not tok: return ''
    k = tok['by_kind']; tot = tok['total_tokens']
    pub = {'sq-garage': 'SQ', 'Sq': 'SQ', 'iot': 'IoT', 'flowtrace': 'flowtrace', 'phosphor': 'PHOSPHOR wall', 'alertboard': 'Alert board', 'macwatch': 'macwatch', 'netdash': 'netdash', 'partswatch': 'partswatch', 'fleet-patch': 'fleet-patch', 'lanwatch': 'lanwatch', 'inbox': 'Inbox hub', 'obd-cable-protocol-re': 'SQ', 'workout': 'Coach Claude', 'ahk02x-site': 'ahk02x.dev'}  # SQ = the car, its app and the cable RE: one project
    merged = collections.Counter()
    for p in tok['top_projects']:
        if p['project'] in pub: merged[pub[p['project']]] += p['tokens']
    shares = merged.most_common()
    rest = tot - sum(t for _, t in shares); shares.append(('Private projects', rest)); mx = max(t for _, t in shares)
    bars = ''.join(f'<div>{html.escape(n)}</div><div class="b"><i style="width:{100*t/mx:.1f}%"></i></div><div class="n">{t/1e9:.2f} B</div>' for n, t in shares)
    first = (tok.get('first') or '')[:7]
    return f'''<section id="built" class="card" style="margin-top:28px"><div class="head">{GLYPHS["tokens"]}<h3>Built with AI assistance</h3></div>
<style>
#built .lead{{font-size:clamp(1.15rem,2.2vw,1.45rem);line-height:1.45;font-weight:600;max-width:46rem;margin:6px 0 18px;padding-left:16px;border-left:5px solid var(--st-built)}}
#built .lead em{{font-style:normal;color:var(--st-built)}}
#built .roles{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:0 0 16px;padding:0;list-style:none}}
#built .roles li{{padding:14px 16px;border:1px solid var(--soft-line);border-top:4px solid var(--c);border-radius:8px;line-height:1.45}}
#built .roles b{{display:block;font:11px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--c);margin-bottom:4px}}
#built .result{{max-width:46rem;margin:0 0 6px}}
#built .src{{font-size:.86rem;color:var(--muted);margin:0 0 4px}}
#built .tile:nth-child(1){{--c:var(--st-built)}}#built .tile:nth-child(2){{--c:var(--st-run)}}#built .tile:nth-child(3){{--c:var(--st-written)}}#built .tile:nth-child(4){{--c:var(--st-live)}}
#built .tile{{border-top:4px solid var(--c)}}#built .tile .v{{color:var(--c)}}
#built .bars>div:nth-child(12n+2) i{{background:var(--st-built)}}#built .bars>div:nth-child(12n+5) i{{background:var(--st-run)}}#built .bars>div:nth-child(12n+8) i{{background:var(--st-written)}}#built .bars>div:nth-child(12n+11) i{{background:var(--st-live)}}
#built .bars .b{{border-color:var(--soft-line)}}
@media (max-width:720px){{#built .roles{{grid-template-columns:1fr}}}}
</style>
<p class="lead">I had the ideas long before I had the time to learn every field they needed. Working with an AI agent <em>took that ceiling off.</em></p>
<ul class="roles"><li style="--c:var(--st-built)"><b>I</b>set the direction and the standard.</li><li style="--c:var(--st-run)"><b>The agent</b>does the legwork.</li><li style="--c:var(--st-written)"><b>I</b>read, test and own what ships.</li></ul>
<p class="result">The projects on this page are the result &mdash; and so is the way of working behind them, which is the part I have learned the most from.</p>
<p class="src">The same count the home page shows: Claude Code transcripts on this Mac since {first}, plus GPT, deduplicated.</p>
<div class="tiles"><div class="tile"><div class="k">Lifetime tokens</div><div class="v">{(_ct+_gt+_lt)/1e9:.2f}<small>billion</small></div><div class="t">Claude {_ct/1e9:.2f} B · GPT {_gt/1e9:.2f} B · others {_lt/1e6:.1f} M</div></div><div class="tile"><div class="k">Sessions</div><div class="v">{tok["sessions"]:,}</div></div><div class="tile"><div class="k">Replies</div><div class="v">{tok["assistant_messages"]:,}</div></div><div class="tile"><div class="k">Cache reads</div><div class="v">{k.get("cache_read_input_tokens",0)/1e9:.2f}<small>billion</small></div><div class="t">fresh input {(k.get("input_tokens",0)+k.get("cache_creation_input_tokens",0))/1e6:,.0f} M · output {k.get("output_tokens",0)/1e6:,.0f} M</div></div></div>
<div class="eyebrow" style="margin-top:26px">By project · Claude Code</div><div class="bars">{bars}</div>
<p class="muted" style="margin-top:12px;font-size:.86rem">Counted by <a href="https://github.com/ahk02x/ahk02x.github.io/blob/main/tools/tokens.py">tools/tokens.py</a>. Streamed messages are deduplicated; a session's tokens are split evenly across the project folders it touched. Private projects are summed, never named. Sessions, replies, cache reads and the project split count the Claude Code side only; the GPT figure is mostly an estimate of ChatGPT web use since 2023; &ldquo;others&rdquo; is local open models on my own GPU, mostly the Crucix lab, read from the model server&rsquo;s log. Totals include cache reads; these are usage counters, not unique generated words or a cost estimate.</p></section>'''
gtok = json.load(open('data/gpt_tokens.json')) if os.path.exists('data/gpt_tokens.json') else {}
ghist = json.load(open('data/gpt_history.json')) if os.path.exists('data/gpt_history.json') else {}  # ChatGPT web estimate (2023 on), tools/gpt_history.py
ltok = json.load(open('data/local_tokens.json')) if os.path.exists('data/local_tokens.json') else {}  # local open models (Crucix et al.), measured from the ollama journal
_ct, _gt = (tok or {}).get('total_tokens', 0), gtok.get('total_tokens', 0) + ghist.get('tokens', 0); _lt = ltok.get('total_tokens', 0); _mx = max(_ct, _gt, 1)
def activity():
    import datetime as dt
    days = collections.Counter()
    for d in (tok or {}).get('by_day', []): days[d['day']] += d['tokens']
    for d, v in gtok.get('by_day', {}).items(): days[d] += v
    for d, v in ghist.get('by_day', {}).items(): days[d] += v
    if not days: return '', ''
    today = dt.date.fromisoformat(max(max(days), gtok.get('updated', '0000')[:10]))
    on = sorted(dt.date.fromisoformat(d) for d, v in days.items() if v)
    best = run = 0; prev = None
    for d in on:
        run = run + 1 if prev and (d - prev).days == 1 else 1; best = max(best, run); prev = d
    cur = 0; d = today
    while days.get(d.isoformat()): cur += 1; d -= dt.timedelta(days=1)
    if not cur and days.get((today - dt.timedelta(days=1)).isoformat()):
        d = today - dt.timedelta(days=1)
        while days.get(d.isoformat()): cur += 1; d -= dt.timedelta(days=1)
    def short(n): return f"{n/1e9:.2f}B" if n >= 1e9 else f"{n/1e6:.1f}M" if n >= 1e6 else f"{n:,}"
    lt = (tok or {}).get('longest_task_min', 0)
    stats = [(short(_ct + _gt + _lt), 'Lifetime tokens'), (short(max(days.values())), 'Peak day'),
             (f"{lt//60}h {lt%60:02d}m" if lt else '—', 'Longest task'), (f"{best} days", 'Longest streak'), (f"{cur} days", 'Current streak')]
    strip = ''.join(f'<div><b>{v}</b><span>{k}</span></div>' for v, k in stats)
    return strip, grid_html(days, today)
def grid_html(days, today):
    import datetime as dt
    nz = sorted(v for v in days.values() if v); q = [nz[int(len(nz) * f)] for f in (.25, .5, .75, .9)] if nz else [1] * 4
    start = today - dt.timedelta(days=7 * 52 + (today.weekday() + 1) % 7)
    cells = []; months = []; d = start; col = 0
    while d <= today:
        if d.weekday() == 6 or d == start:
            if d.day <= 7: months.append(f'<span style="grid-column:{col + 1}">{d.strftime("%b")}</span>')
            col += 1
        v = days.get(d.isoformat(), 0); lvl = 0 if not v else 1 + sum(v > x for x in q)
        cells.append(f'<i class="l{lvl}" style="grid-column:{col};grid-row:{(d.weekday() + 1) % 7 + 1}" title="{d.isoformat()}: {v:,}"></i>')
        d += dt.timedelta(days=1)
    def sh(n): return f"{n/1e9:.1f}B" if n >= 1e9 else f"{n/1e6:.0f}M" if n >= 1e6 else f"{n/1e3:.0f}K" if n >= 1e3 else f"{n}"
    tips = ['none'] + [f"up to {sh(q[0])}"] + [f"{sh(a)}–{sh(b)}" for a, b in zip(q, q[1:])] + [f"over {sh(q[-1])}"]
    key = '<div class="hm-k">More' + ''.join(f'<i class="l{i}" title="{t} / day"></i>' for i, t in reversed(list(enumerate(tips)))) + 'Less</div>'
    return f'<div class="hm" style="--cols:{col}">' + ''.join(cells) + f'</div><div class="hm-m" style="--cols:{col}">' + ''.join(months) + '</div>' + key
SQ_REPOS = ('sq-garage', 'Sq', 'obd-cable-protocol-re')  # the car, its app and the cable RE: one project
def sq_month_bars():
    """Monthly AI-session spend on the SQ repos — the build month, then the taper."""
    by_proj = (tok or {}).get('by_month_project') or {}
    months = collections.Counter()
    for repo in SQ_REPOS:
        for m in by_proj.get(repo, []): months[m['month']] += m['tokens']
    months = {m: v for m, v in months.items() if v}
    if not months: return ''
    mx = max(months.values()); this_month = (tok.get('last') or '')[:7]
    rows = ''
    for ym in sorted(months):
        try: lbl = datetime.date(int(ym[:4]), int(ym[5:7]), 1).strftime('%b %Y')
        except ValueError: lbl = ym
        if ym == this_month: lbl += ' <small>so far</small>'
        rows += f'<div>{lbl}</div><div class="b"><i style="width:{100*months[ym]/mx:.1f}%"></i></div><div class="n">{months[ym]/1e9:.2f} B</div>'
    return f'<div class="bars">{rows}</div>'
def gh_grid():
    import datetime as dt
    g = json.load(open('data/github.json')) if os.path.exists('data/github.json') else {}
    if not g: return ''
    return grid_html(collections.Counter(g['by_day']), dt.date.fromisoformat(max(max(g['by_day']), gtok.get('updated', '0000')[:10])))
def _next_update():
    import datetime as dt
    from zoneinfo import ZoneInfo
    tz = ZoneInfo('America/Toronto'); now = dt.datetime.now(tz)
    return (now.date() + dt.timedelta(days=1)).isoformat() + ' 00:00 ET'
subs = {'{{claude_tokens}}': f"{_ct:,}" if _ct else '—', '{{gpt_tokens}}': f"{_gt:,}" if _gt else '—',
        '{{claude_pct}}': f"{max(_ct/_mx*100, 1 if _ct else 0):.1f}", '{{gpt_pct}}': f"{max(_gt/_mx*100, 1 if _gt else 0):.1f}",
        '{{tokens_updated}}': (gtok.get('updated', '') + ' ET') if gtok.get('updated') else '—',
        '{{tokens_next}}': _next_update(),
        '{{gpt_note}}': f" · GPT includes ~{ghist['tokens']/1e6:,.0f}M estimated ChatGPT use since {ghist.get('since', '2023')}" if ghist.get('tokens') else '',
        '{{sq_months}}': sq_month_bars(),
        '{{tk_strip}}': activity()[0], '{{tk_grid}}': activity()[1], '{{gh_grid}}': gh_grid(), '{{gh_total}}': str((json.load(open('data/github.json')) if os.path.exists('data/github.json') else {}).get('total', '—')),
        '{{tokens_b}}': f"{tok.get('total_tokens',0)/1e9:.2f}" if tok else '—', '{{sessions}}': f"{tok.get('sessions',0):,}" if tok else '—',
        '{{sq_word}}': word, '{{sq_cls}}': cls, '{{sq_window}}': ' to '.join(hc.get('window', ['', ''])), '{{token_card}}': token_card(),
        '{{tokens_since}}': (tok.get('first') or '')[:7], '{{sq_generated}}': html.escape(hc.get('generated', ''))}
for g, svg in GLYPHS.items(): subs['{{glyph:' + g + '}}'] = svg
entries = []
for src in sorted(glob.glob('src/pages/*.html')):
    raw = open(src).read(); fm, body = raw.split('\n---\n', 1)
    meta = dict(re.findall(r'^(\w+):\s*(.*)$', fm, re.M))
    m = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})"', body)
    entries.append({'meta': meta, 'body': body.strip(), 'date': m.group(1) if m else ''})
posts = sorted([e for e in entries if e['meta']['path'].startswith('/writing/') and e['meta']['path'] != '/writing/'],
               key=lambda e: (e['date'], int(e['meta'].get('note', '0') or 0)), reverse=True)
def when(d):
    try: return datetime.date.fromisoformat(d).strftime('%b %Y')
    except ValueError: return ''
def post_item(e):
    mt = e['meta']; blurb = mt.get('summary') or mt.get('description', '')
    return (f'<div class="item"><div class="t"><a href="{mt["path"]}">{html.escape(mt["title"])}</a></div>'
            f'<time datetime="{e["date"]}">{when(e["date"])}</time><p class="d">{html.escape(blurb)}</p></div>')
subs['{{writing_list}}'] = ''.join(post_item(e) for e in posts)
def when_long(d):
    try: return datetime.date.fromisoformat(d).strftime('%B %Y')
    except ValueError: return ''
subs['{{latest_notes}}'] = ''.join(f'<a class="article-link" href="{e["meta"]["path"]}"><span>{when_long(e["date"])} · Field note {int(e["meta"].get("note", "0") or 0):03}</span><strong>{html.escape(e["meta"]["title"])} <span aria-hidden="true">↗</span></strong></a>' for e in posts[:3])
# Structured data (schema.org JSON-LD): the site and its author on every page, the About page as his
# profile, each write-up as an Article he wrote. alternateName carries the full name in the spellings
# people actually type, so a search for any of them matches these pages.
SITE = 'https://ahk02x.dev'
PERSON_ID, WEBSITE_ID = SITE + '/#person', SITE + '/#website'
PERSON = {'@type': 'Person', '@id': PERSON_ID, 'name': 'Amir Khademi',
          'alternateName': ['Amir Hossein Khademi', 'Amir-Hossein Khademi', 'Amirhossein Khademi'],
          'givenName': 'Amir Hossein', 'familyName': 'Khademi',
          'url': SITE + '/', 'mainEntityOfPage': SITE + '/about.html',
          'jobTitle': 'Site Reliability Engineer',
          'description': 'Site Reliability Engineer. Writes about car telemetry, home infrastructure and agent tooling at ahk02x.dev.',
          'email': 'mailto:amir@ahk02x.com',
          'knowsAbout': ['Site reliability engineering', 'Linux', 'Kubernetes', 'Observability', 'Payments infrastructure', 'Identity and access management', 'Home infrastructure', 'Vehicle telemetry', 'AI agent tooling'],
          'sameAs': ['https://github.com/ahk02x', 'https://www.linkedin.com/in/amirh-khademi/']}
WEBSITE = {'@type': 'WebSite', '@id': WEBSITE_ID, 'url': SITE + '/', 'name': 'ahk02x — field notes',
           'alternateName': 'Amir Khademi — field notes', 'inLanguage': 'en',
           'author': {'@id': PERSON_ID}, 'publisher': {'@id': PERSON_ID}}
def jsonld(meta, body):
    url = SITE + meta['path']; graph = [WEBSITE, PERSON]
    date = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})"', body)
    if meta['path'] == '/about.html':
        graph.append({'@type': 'ProfilePage', '@id': url, 'url': url, 'name': meta['title'], 'description': meta.get('description', ''),
                      'isPartOf': {'@id': WEBSITE_ID}, 'mainEntity': {'@id': PERSON_ID}})
    elif meta['path'].startswith('/writing/') and date:
        art = {'@type': 'Article', '@id': url + '#article', 'url': url, 'mainEntityOfPage': url, 'headline': meta['title'],
               'description': meta.get('description', ''), 'datePublished': date.group(1), 'inLanguage': 'en',
               'author': {'@id': PERSON_ID}, 'publisher': {'@id': PERSON_ID}, 'isPartOf': {'@id': WEBSITE_ID}}
        if os.path.exists('assets/og.png'): art['image'] = SITE + '/assets/og.png'
        graph.append(art)
    else:
        graph.append({'@type': 'WebPage', '@id': url, 'url': url, 'name': meta['title'], 'description': meta.get('description', ''),
                      'isPartOf': {'@id': WEBSITE_ID}, 'about': {'@id': PERSON_ID}})
    data = json.dumps({'@context': 'https://schema.org', '@graph': graph}, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    return '<script type="application/ld+json">' + data + '</script>\n'
def bare(title, desc, path, body, extra_head=''):
    """Full-screen pages (the drawer home): same head and metadata, own stylesheet, no shared header."""
    full = chrome(title, desc, path, '', path, extra_head)
    head = full.split('<body>')[0].replace('<link rel="stylesheet" href="/style.css">', '<link rel="stylesheet" href="/assets/home.css">')
    head = re.sub(r'<link rel="preconnect"[^\n]*\n<link rel="stylesheet" href="https://fonts[^\n]*\n', '', head)
    head = head.replace('<script src="/assets/site.js" defer></script>', '<script src="/assets/home.js" defer></script>').replace('#f2f0e9', '#d4d5d1')
    return head + '<body class="bare">\n' + body + '\n</body>\n</html>'
def bust(page):
    """Content-hash every local CSS/JS link, so new HTML never pairs with a stylesheet an edge or browser cached earlier."""
    import hashlib
    def ver(m):
        path = m.group(2)
        try: v = hashlib.sha256(open(path.lstrip('/'), 'rb').read()).hexdigest()[:10]
        except OSError: return m.group(0)
        return f'{m.group(1)}{path}?v={v}"'
    return re.sub(r'((?:href|src)=")(/(?:style\.css|assets/[\w.-]+\.(?:css|js)))"', ver, page)
pages = []
for e in entries:
    meta, body = e['meta'], e['body']
    for a, b in subs.items(): body = body.replace(a, b)
    if meta['path'].startswith('/sq/'):  # one tab strip is the only navigation between SQ pages
        tabs = [('/sq/', 'Overview'), ('/sq/health.html', 'Weekly health'), ('/sq/trends.html', 'Trends'), ('/sq/gallery.html', 'Gallery'), ('/sq/build-log.html', 'Build log')]
        strip = '<nav class="sq-tabs" aria-label="SQ5 sections">' + ''.join(
            f'<a href="{h}"{" aria-current=\"page\"" if h == meta["path"] else ""}>{t}</a>' for h, t in tabs) + '</nav>'
        body = body.replace('</section>', '</section>' + strip, 1)
    if 'id="main"' not in body:
        body = body.replace('<main ', '<main id="main" ', 1)
    body = body.replace('<main id="main" class="wrap', '<main id="main" class="wrap inner-page')
    if meta['path'].startswith('/writing/') and '<time datetime=' in body and 'class="byline"' not in body:
        body = body.replace('</h1>', '</h1><p class="byline">By <a href="/about.html">Amir Khademi</a></p>', 1)
    if meta.get('layout') == 'bare':
        out = bare(meta['title'], meta.get('description', ''), meta['path'], body, jsonld(meta, body))
    else:
        out = chrome(meta['title'], meta.get('description', ''), meta['path'], body, meta.get('nav', meta['path']), jsonld(meta, body))
    dest = meta['path'].lstrip('/') or 'index.html'
    if dest.endswith('/'): dest += 'index.html'
    os.makedirs(os.path.dirname(dest) or '.', exist_ok=True); open(dest, 'w').write(bust(out)); pages.append(meta['path'])
def rfc822(d):
    try: return datetime.datetime.fromisoformat(d).replace(tzinfo=datetime.timezone.utc).strftime('%a, %d %b %Y 00:00:00 +0000')
    except ValueError: return ''
feed_items = ''.join(f'<item><title>{html.escape(e["meta"]["title"])}</title><link>https://ahk02x.dev{e["meta"]["path"]}</link><guid isPermaLink="true">https://ahk02x.dev{e["meta"]["path"]}</guid>'
                     + (f'<pubDate>{rfc822(e["date"])}</pubDate>' if e['date'] else '') + f'<description>{html.escape(e["meta"].get("description", ""))}</description></item>\n' for e in posts)
open('feed.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>ahk02x — field notes</title><link>https://ahk02x.dev/</link><atom:link href="https://ahk02x.dev/feed.xml" rel="self" type="application/rss+xml"/><description>Engineering write-ups by Amir Khademi: car telemetry, home infrastructure, and tools that have to earn your trust.</description><language>en</language>\n' + feed_items + '</channel></rss>\n')
open('sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>https://ahk02x.dev{p}</loc></url>\n' for p in pages if not p.startswith('/404')) + '</urlset>\n')
print('built', len(pages), 'pages:', ' '.join(pages))


# Preview/deploy only the public site, never source files or operator scripts.
public_root = '_site'
os.makedirs(public_root, exist_ok=True)
for entry in os.scandir(public_root):
    if entry.is_dir():
        shutil.rmtree(entry.path)
    else:
        os.unlink(entry.path)
public_files = ['style.css', 'robots.txt', '.well-known/security.txt', 'sitemap.xml', 'feed.xml', 'CNAME', '.nojekyll', 'data/tokens.json', 'data/gpt_tokens.json', 'data/github.json', 'data/sq_trends.json', 'sq/health.json']
public_files += [(p.lstrip('/') or 'index.html') + ('index.html' if p.endswith('/') and p != '/' else '') for p in pages]
public_files += [p for p in glob.glob('assets/*') + glob.glob('assets/sq-gallery/*') + glob.glob('assets/infra/*') if os.path.isfile(p)]
public_files += [p for p in glob.glob('*.txt') if re.fullmatch(r'[0-9a-f]{32}\.txt', p)]  # IndexNow key, see tools/indexnow.py
for source in public_files:
    if os.path.exists(source):
        dest = os.path.join(public_root, source)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(source, dest)
