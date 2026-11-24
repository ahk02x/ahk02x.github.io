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
# The numbered directory. The header, the footer and the pages' own eyebrows all use these plate numbers;
# 05 is Contact, a mailto that sits after the page links, so the nav reads 01 02 03 04 06 05.
SECTIONS = [('01', '/about.html', 'About'), ('02', '/projects/', 'Projects'), ('03', '/infra.html', 'Infra'), ('04', '/writing/', 'Writing'), ('06', '/ask/', 'ahkira')]
CONTACT = ('05', 'mailto:amir@ahk02x.com', 'Contact')
NAV = [('/', 'Home'), ('/projects/', 'Projects'), ('/infra.html', 'Infra'), ('/writing/', 'Writing'), ('/about.html', 'About')]
# The SQ tabs, in reading order: the strip at the top of every SQ page and the Next row at the bottom both use it.
SQ_TABS = [('/sq/', 'Overview'), ('/sq/logger.html', 'Logger'), ('/sq/health.html', 'Weekly health'), ('/sq/trends.html', 'Trends'), ('/sq/gallery.html', 'Gallery'), ('/sq/build-log.html', 'Build log')]
MARK = '<svg viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round"><circle cx="64" cy="64" r="46"/><path d="M36,82 H54 C64,82 64,46 74,46 H92"/><path d="M36,46 H54 C64,46 64,82 74,82 H92"/></g></svg>'
def glyph_svg(body, sw=10):  # one line-icon language: 128 box, round caps, currentColor so the row's status tints it
    return f'<svg class="glyph" viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">{body}</g></svg>'
def dot(cx, cy, r): return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="currentColor" stroke-width="2"/>'
# One glyph per project, drawn from what the project does. The Crossing mark stays the owner's alone (MARK), never a row icon.
GLYPHS = {
 'alert': glyph_svg('<path d="M26,92 C34,84 38,72 38,56 C38,40 49,28 64,28 C79,28 90,40 90,56 C90,72 94,84 102,92 Z"/><path d="M64,28 V18"/><path d="M52,104 C54,112 74,112 76,104"/><path d="M52,60 l9,9 l17,-19"/>'),
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
 'helmet': glyph_svg('<path d="M18,88 C18,48 42,22 74,22 C98,22 112,40 112,64 V88 A6,6 0 0 1 106,94 H24 A6,6 0 0 1 18,88 Z"/><path d="M58,50 H112 V72 H64 A6,6 0 0 1 58,66 Z"/>' + dot(96, 61, 5)),
 'tiles': glyph_svg('<rect x="18" y="18" width="38" height="38" rx="4"/><rect x="72" y="18" width="38" height="38" rx="4"/><rect x="18" y="72" width="38" height="38" rx="4"/><rect x="72" y="72" width="38" height="38" rx="4" fill="currentColor"/>'),
 'chat': glyph_svg('<path d="M18,30 A8,8 0 0 1 26,22 H102 A8,8 0 0 1 110,30 V78 A8,8 0 0 1 102,86 H52 L30,106 V86 H26 A8,8 0 0 1 18,78 Z"/>' + dot(45, 54, 6) + dot(64, 54, 6) + dot(83, 54, 6)),
 'code': glyph_svg('<path d="M42,34 L14,64 L42,94"/><path d="M86,34 L114,64 L86,94"/><path d="M72,24 L56,104"/>'),
 'plug': glyph_svg('<g transform="rotate(40 64 64)"><rect x="38" y="40" width="52" height="40" rx="8"/><path d="M52,40 V20 M76,40 V20"/><path d="M64,80 V112"/></g>'),
 'cert': glyph_svg('<path d="M64,12 L104,26 V60 C104,88 86,106 64,116 C42,106 24,88 24,60 V26 Z"/><path d="M46,62 l12,12 l24,-26"/>'),
 'bench': glyph_svg('<rect x="10" y="34" width="108" height="56" rx="8"/><circle cx="42" cy="62" r="14"/><circle cx="86" cy="62" r="14"/><path d="M24,90 V106 M40,90 V106 M56,90 V106"/>'),
 'tokens': glyph_svg('<path d="M30,106 V82"/><path d="M64,106 V56"/><path d="M98,106 V26"/>', 17),
 'tag': glyph_svg('<path d="M22,22 H66 L106,62 L62,106 L22,66 Z"/>' + dot(44, 44, 7)),
 'sq': '<span class="sq-brand"><img class="glyph sq sq-dark" src="/assets/sq-mark-dark.svg" alt="" width="34" height="34"><img class="glyph sq sq-light" src="/assets/sq-mark-light.svg" alt="" width="34" height="34"></span>',
}
def chrome(title, desc, path, body, nav_key, extra_head=''):
    if 'Amir Khademi' not in title and title != 'Not found': title = f'{title} · Amir Khademi'  # every indexed page carries the author's name
    # nav_key is the page's `nav:` front matter (the SQ pages file under Projects) or its own path.
    sec = next((h for _, h, _ in SECTIONS if (nav_key or path).startswith(h)), '')
    nav = ''.join(f'<a href="{h}"' + (' aria-current="page"' if h == sec else '') + f'><span class="nav-no" aria-hidden="true">{n}</span> {t}</a>' for n, h, t in SECTIONS)
    nav += f'<a href="{CONTACT[1]}"><span class="nav-no" aria-hidden="true">{CONTACT[0]}</span> {CONTACT[2]} <span aria-hidden="true">↗</span></a>'
    directory = ''.join(f'<a href="{h}">{n} {t}</a>' for n, h, t in SECTIONS)
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
<link rel="preload" href="/assets/fonts/geist-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="/assets/fonts/geist-mono-latin.woff2" as="font" type="font/woff2" crossorigin>
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
<header class="site-header"><a class="site-brand" href="/"><span>AHK / 02X</span> <span>Personal archive</span></a><nav class="site-nav" aria-label="Main navigation">{nav}<button class="theme-toggle" type="button" hidden><span data-theme-label>Dark</span></button></nav></header>
{body}
<footer class="site-footer"><div><span class="eyebrow">{CONTACT[0]} / {CONTACT[2]}</span><a href="{CONTACT[1]}">amir@ahk02x.com <span aria-hidden="true">↗</span></a><span>Amir Khademi · online as ahk02x</span></div><nav aria-label="Directory"><span class="eyebrow">Directory</span>{directory}</nav><nav class="social-links" aria-label="Social profiles"><span class="eyebrow">Elsewhere</span><a href="https://x.com/ahk02x" rel="me">X <span aria-hidden="true">↗</span></a><a href="https://www.linkedin.com/in/amirh-khademi/" rel="me">LinkedIn <span aria-hidden="true">↗</span></a><a href="https://github.com/ahk02x" rel="me">GitHub <span aria-hidden="true">↗</span></a></nav></footer>
</div>
</body>
</html>'''
def token_card():
    if not tok: return ''
    k = tok['by_kind']; tot = tok['total_tokens']
    pub = {'sq-garage': 'SQ', 'Sq': 'SQ', 'iot': 'IoT', 'flowtrace': 'flowtrace', 'alertboard': 'Alert board', 'macwatch': 'macwatch', 'netdash': 'netdash', 'partswatch': 'partswatch', 'fleet-patch': 'fleet-patch', 'lanwatch': 'lanwatch', 'inbox': 'Inbox hub', 'obd-cable-protocol-re': 'SQ', 'workout': 'Coach Claude', 'ahk02x-site': 'ahk02x.dev', 'Crucix': 'Crucix', 'certguard': 'certguard', 'llmbench': 'llmbench', 'ahkira': 'ahkira', 'ahkira-bot': 'ahkira', 'sentry': 'sentry', 'sq-logger': 'SQ', 'sq-audio': 'SQ'}  # SQ = the car, its app and the cable RE: one project
    merged = collections.Counter()
    # every tool, not just Claude Code: Claude + GPT (Codex) + open models on my own GPUs
    for p in tok['top_projects'] + gtok.get('top_projects', []):
        if p['project'] in pub: merged[pub[p['project']]] += p['tokens']
    for n, t in ltok.get('sources', {}).get('lab', {}).get('by_project', {}).items():
        if n in pub: merged[pub[n]] += t
    tot = _ct + _gt + _lt
    shares = merged.most_common()
    rest = tot - sum(t for _, t in shares); shares.append(('Private projects', rest)); mx = max(t for _, t in shares)
    bars = ''.join(f'<div>{html.escape(n)}</div><div class="b"><i style="width:{100*t/mx:.1f}%"></i></div><div class="n">{t/1e9:.2f} B</div>' for n, t in shares)
    first = (tok.get('first') or '')[:7]
    # Theme: no card, no radius, no fills. A band with a hairline role list, a .statrow and the .bars idiom.
    # Every number and every sentence below is the site's account of its own data: restyle, never reword.
    return f'''<section id="tokens" class="band">
<style>
#tokens{{display:flex;flex-direction:column;gap:24px}}
#tokens>*,#tokens .spec,#tokens .bars{{margin:0}}
#tokens>p,#tokens .two-up p{{max-width:64ch}}
#tokens .two-up>div{{display:flex;flex-direction:column;gap:16px}}
#tokens .statrow small{{display:block;color:var(--quiet)}}
</style>
<div class="band-head"><div><span class="eyebrow">Built with AI assistance</span><h2>I had the ideas long before I had the time to learn every field they needed. Working with an AI agent took that ceiling off.</h2></div></div>
<div class="two-up"><div><dl class="spec"><dt>I</dt><dd>set the direction and the standard.</dd><dt>The agent</dt><dd>does the legwork.</dd><dt>I</dt><dd>read, test and own what ships.</dd></dl>
<p>The projects on this page are the result, and so is the way of working behind them, which is the part I have learned the most from.</p>
<p class="muted">The same count the home page shows: Claude Code transcripts on this Mac since {first}, plus GPT, deduplicated.</p></div>
<div><div class="eyebrow">By project · every tool</div><div class="bars">{bars}</div></div></div>
<div class="statrow"><div><span>Lifetime tokens</span><b>{(_ct+_gt+_lt)/1e9:.2f} billion</b><small>Claude {_ct/1e9:.2f} B · GPT {_gt/1e9:.2f} B · others {_lt/1e6:.1f} M</small></div><div><span>Sessions</span><b>{tok["sessions"]:,}</b></div><div><span>Replies</span><b>{tok["assistant_messages"]:,}</b></div><div><span>Cache reads</span><b>{k.get("cache_read_input_tokens",0)/1e9:.2f} billion</b><small>fresh input {(k.get("input_tokens",0)+k.get("cache_creation_input_tokens",0))/1e6:,.0f} M · output {k.get("output_tokens",0)/1e6:,.0f} M</small></div></div>
<p class="muted">Counted by <a href="https://github.com/ahk02x/ahk02x.github.io/blob/main/tools/tokens.py">tools/tokens.py</a>. Streamed messages are deduplicated; a session's tokens are split evenly across the project folders it touched. Private projects are summed, never named. Sessions, replies and cache reads count the Claude Code side only; the project split counts Claude, GPT and my own GPUs, and ChatGPT web use, which has no project, sits in Private projects; the GPT figure is mostly an estimate of ChatGPT web use since 2023; &ldquo;others&rdquo; is local open models on my own GPUs: mostly the Crucix lab, read from the model server&rsquo;s log, plus a private chat app on my 3080, counted from its own usage ledger. Totals include cache reads; these are usage counters, not unique generated words or a cost estimate.</p></section>'''
gtok = json.load(open('data/gpt_tokens.json')) if os.path.exists('data/gpt_tokens.json') else {}
ghist = json.load(open('data/gpt_history.json')) if os.path.exists('data/gpt_history.json') else {}  # ChatGPT web estimate (2023 on), tools/gpt_history.py
ltok = json.load(open('data/local_tokens.json')) if os.path.exists('data/local_tokens.json') else {}  # local open models: Crucix lab (fixed, from the ollama journal) + the 3080 chat app (tools/local_tokens.py)
_ct, _gt = (tok or {}).get('total_tokens', 0), gtok.get('total_tokens', 0) + ghist.get('tokens', 0); _lt = ltok.get('total_tokens', 0); _mx = max(_ct, _gt, 1)
def activity():
    """The AI-token activity snapshot: stats strip, heatmap, and the dated facts the home page quotes."""
    import datetime as dt
    days = collections.Counter()
    for d in (tok or {}).get('by_day', []): days[d['day']] += d['tokens']
    for d, v in gtok.get('by_day', {}).items(): days[d] += v
    for d, v in ghist.get('by_day', {}).items(): days[d] += v
    if not days: return {}
    today = dt.date.fromisoformat(max(max(days), gtok.get('updated', '0000')[:10]))
    on = sorted(dt.date.fromisoformat(d) for d, v in days.items() if v)
    best = run = 0; prev = None
    for d in on:
        run = run + 1 if prev and (d - prev).days == 1 else 1; best = max(best, run); prev = d
    # The current streak ends on the snapshot day, or the day before it if that day has no data yet.
    end = today if days.get(today.isoformat()) else today - dt.timedelta(days=1)
    cur = 0; d = end
    while days.get(d.isoformat()): cur += 1; d -= dt.timedelta(days=1)
    def short(n): return f"{n/1e9:.2f}B" if n >= 1e9 else f"{n/1e6:.1f}M" if n >= 1e6 else f"{n:,}"
    lt = (tok or {}).get('longest_task_min', 0)
    stats = [(short(_ct + _gt + _lt), 'Lifetime tokens'), (short(max(days.values())), 'Peak day'),
             (f"{lt//60}h {lt%60:02d}m" if lt else '—', 'Longest task'), (f"{best} days", 'Longest streak'), (f"{cur} days", 'Current streak')]
    strip = ''.join(f'<div><b>{v}</b><span>{k}</span></div>' for v, k in stats)
    return {'strip': strip, 'grid': grid_html(days, today), 'today': today, 'streak': cur, 'streak_end': end}
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
def _day_short(value):
    """A date a reader can hold: '11 Nov'. The counters are daily, so the clock and zone are noise."""
    try: return datetime.date.fromisoformat(value[:10]).strftime('%-d %b')
    except (TypeError, ValueError): return '—'
def _next_update():
    import datetime as dt
    from zoneinfo import ZoneInfo
    tz = ZoneInfo('America/Toronto'); now = dt.datetime.now(tz)
    return (now.date() + dt.timedelta(days=1)).strftime('%-d %b')  # the counters refresh overnight, Toronto time
_act = activity()
def sq_through(week):
    """The last day the snapshot covers: its weeks are whole Mon-Sun ones, so it is good through that Sunday."""
    try: d = datetime.date.fromisoformat(week) + datetime.timedelta(days=6)
    except (TypeError, ValueError): return '—'
    return d.strftime('%-d %B %Y')
def sq_facts():
    """The SQ figures the home page quotes, from the committed trends snapshot and the token export. Missing = a dash."""
    t = json.load(open('data/sq_trends.json')) if os.path.exists('data/sq_trends.json') else {}
    tot = t.get('totals') or {}
    hours = tot.get('hours'); weeks = sum(1 for w in t.get('weeks', []) if w.get('hours'))
    spent = sum(p['tokens'] for p in (tok or {}).get('top_projects', []) if p['project'] in SQ_REPOS)
    num = lambda v: f"{v:,}" if isinstance(v, int) else '—'
    # Every drive figure on the SQ pages comes from this one snapshot, so no page can quote a stale count.
    # The snapshot is whole weeks only (tools/sq_trends.py): the date it is good through is printed with it.
    return {'{{sq_hours}}': f"{hours:,.1f}" if isinstance(hours, (int, float)) else '—', '{{sq_weeks}}': str(weeks) if weeks else '—',
            '{{sq_tokens}}': f"{spent/1e9:.2f}B" if spent else '—',
            '{{sq_captures}}': num(tot.get('captures')), '{{sq_samples}}': num(tot.get('samples')),
            '{{sq_through}}': sq_through(t.get('through_week')), **sq_live(t)}
def sq_live(t):
    """The two SQ readouts that move every week: last week's driving and its misfire rate, from data/sq_trends.json,
    which the publish job refreshes with the health card. The verdict itself stays on the card. Missing = a dash."""
    driven = [w for w in t.get('weeks', []) if w.get('hours') and isinstance(w.get('misfire_hr'), (int, float))]
    last, prev = (driven[-1] if driven else {}), (driven[-2] if len(driven) > 1 else {})
    lm, pm = last.get('misfire_hr'), prev.get('misfire_hr')
    if isinstance(lm, (int, float)) and isinstance(pm, (int, float)) and pm:
        ch = (lm - pm) / pm * 100
        vs = f"{'down' if ch < 0 else 'up'} {abs(ch):.0f}% on the week before ({pm:g} an hour)"
    else:
        vs = 'no earlier week to compare'
    wk = sq_through(last.get('week')) if last else '—'
    hrs, trips = last.get('hours'), last.get('captures')
    return {'{{sq_wk_hours}}': f"{hrs:g}" if isinstance(hrs, (int, float)) else '—',
            '{{sq_wk_trips}}': f"{trips:,}" if isinstance(trips, int) else '—',
            '{{sq_mis_last}}': f"{lm:g}" if isinstance(lm, (int, float)) else '—',
            '{{sq_mis_vs}}': html.escape(vs), '{{sq_mis_week}}': wk}
subs = {'{{claude_tokens}}': f"{_ct:,}" if _ct else '—', '{{gpt_tokens}}': f"{_gt:,}" if _gt else '—',
        '{{claude_pct}}': f"{max(_ct/_mx*100, 1 if _ct else 0):.1f}", '{{gpt_pct}}': f"{max(_gt/_mx*100, 1 if _gt else 0):.1f}",
        '{{tokens_updated}}': _day_short(gtok.get('updated', '')),
        '{{tokens_next}}': _next_update(),
        '{{gpt_note}}': f" · GPT includes ~{ghist['tokens']/1e6:,.0f}M estimated ChatGPT use since {ghist.get('since', '2023')}" if ghist.get('tokens') else '',
        '{{sq_months}}': sq_month_bars(),
        '{{tk_strip}}': _act.get('strip', ''), '{{tk_grid}}': _act.get('grid', ''), '{{gh_grid}}': gh_grid(), '{{gh_total}}': str((json.load(open('data/github.json')) if os.path.exists('data/github.json') else {}).get('total', '—')),
        '{{tokens_b}}': f"{tok.get('total_tokens',0)/1e9:.2f}" if tok else '—', '{{sessions}}': f"{tok.get('sessions',0):,}" if tok else '—',
        '{{sq_word}}': word, '{{sq_cls}}': cls, '{{sq_window}}': ' to '.join(hc.get('window', ['', ''])), '{{token_card}}': token_card(),
        '{{tokens_since}}': (tok.get('first') or '')[:7], '{{sq_generated}}': html.escape(hc.get('generated', ''))}
subs.update(sq_facts())
# Dated by the activity snapshot, not by the clock, so a rebuild on another day changes nothing.
subs['{{snapshot_day}}'] = f"{_act['today'].day} {_act['today'].strftime('%b %Y')}" if _act else '—'
for g, svg in GLYPHS.items(): subs['{{glyph:' + g + '}}'] = svg
entries = []
for src in sorted(glob.glob('src/pages/*.html')):
    raw = open(src).read(); fm, body = raw.split('\n---\n', 1)
    meta = dict(re.findall(r'^(\w+):\s*(.*)$', fm, re.M))
    m = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})"', body)
    entries.append({'meta': meta, 'body': body.strip(), 'date': m.group(1) if m else ''})
posts = sorted([e for e in entries if e['meta']['path'].startswith('/writing/') and e['meta']['path'] != '/writing/' and e['meta'].get('note')],
               key=lambda e: (e['date'], int(e['meta'].get('note', '0') or 0)), reverse=True)
def when(d):
    try: return datetime.date.fromisoformat(d).strftime('%b %Y')
    except ValueError: return ''
# Field notes for projects still running are held back for now: the index shows the title unlinked
# with "Write-up coming soon". The pages still build. Dates and summaries are off the list for now too.
SOON = {'/writing/claude-code-on-call.html', '/writing/memory-as-infrastructure.html', '/writing/fleet-patch.html',
        '/writing/lanwatch.html', '/writing/partswatch.html', '/writing/everything-i-ever-kept.html'}
def post_item(e):
    mt = e['meta']
    # `status` tints the row with the projects-list colour; the chip names the kind, never a date.
    st = mt.get('status', 'written')
    if mt['path'] in SOON:
        return (f'<div class="item st-{st}"><div class="t"><span>{html.escape(mt["title"])}</span></div>'
                f'<span class="chip kind">Write-up coming soon</span></div>')
    label = 'Written' if st == 'written' else 'Built'
    return (f'<div class="item st-{st}"><div class="t"><a href="{mt["path"]}">{html.escape(mt["title"])}</a></div>'
            f'<span class="chip kind">{label}</span></div>')
subs['{{writing_list}}'] = ''.join(post_item(e) for e in sorted(posts, key=lambda e: (e['meta'].get('built') or e['date'][:7], e['date']), reverse=True))
def when_long(d):
    try: return datetime.date.fromisoformat(d).strftime('%B %Y')
    except ValueError: return ''
subs['{{latest_notes}}'] = ''.join(f'<a class="article-link" href="{e["meta"]["path"]}"><span>{when_long(e["date"])} · Field note {int(e["meta"].get("note", "0") or 0):03}</span><strong>{html.escape(e["meta"]["title"])} <span aria-hidden="true">↗</span></strong></a>' for e in posts[:3])
# Home: three notes I picked, in this order, as the writing index's own rows (post_item, untouched), each
# chip prefixed with its field-note number; plus the count and the title the Now panel quotes.
# A path that no longer exists fails the build instead of quietly showing two rows.
HOME_NOTES = ['/writing/go-x509.html', '/writing/memory-as-infrastructure.html', '/writing/ahkira.html']
by_path = {e['meta']['path']: e for e in posts}
home_posts = [by_path[p] for p in HOME_NOTES]
subs['{{latest_rows}}'] = ''.join(post_item(e).replace('class="chip">', f'class="chip">Field note {int(e["meta"].get("note", "0") or 0):03} · ', 1) for e in home_posts)
subs['{{writing_count}}'] = str(len(posts))
subs['{{now_latest}}'] = f'<a href="{posts[0]["meta"]["path"]}">{html.escape(posts[0]["meta"]["title"])}</a>' if posts else '—'
# Structured data (schema.org JSON-LD): the site and its author on every page, the About page as his
# profile, each write-up as an Article he wrote. The public name is Amir Khademi only; the longer
# legal name stays off every page except /photo-rights.html, which a copyright claim points at.
SITE = 'https://ahk02x.dev'
PERSON_ID, WEBSITE_ID = SITE + '/#person', SITE + '/#website'
PERSON = {'@type': 'Person', '@id': PERSON_ID, 'name': 'Amir Khademi',
          'givenName': 'Amir', 'familyName': 'Khademi',
          'url': SITE + '/', 'mainEntityOfPage': SITE + '/about.html',
          'jobTitle': 'Platform Engineer',
          'description': 'Platform Engineer. Writes about car telemetry, home infrastructure and agent tooling at ahk02x.dev.',
          'email': 'mailto:amir@ahk02x.com',
          'knowsAbout': ['Platform engineering', 'Site reliability engineering', 'Linux', 'Kubernetes', 'Observability', 'Identity and access management', 'Home infrastructure', 'Vehicle telemetry', 'AI agent tooling'],
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
def bust(page):
    """Content-hash every local CSS/JS link, so new HTML never pairs with a stylesheet an edge or browser cached earlier."""
    import hashlib
    def ver(m):
        path = m.group(2)
        try: v = hashlib.sha256(open(path.lstrip('/'), 'rb').read()).hexdigest()[:10]
        except OSError: return m.group(0)
        return f'{m.group(1)}{path}?v={v}"'
    return re.sub(r'((?:href|src)=")(/(?:style\.css|assets/[\w.-]+\.(?:css|js)))"', ver, page)
pages = []; hidden = {e['meta']['path'] for e in entries if e['meta'].get('noindex')}  # noindex pages: built, never in the sitemap
for e in entries:
    meta, body = e['meta'], e['body']
    for a, b in subs.items(): body = body.replace(a, b)
    if meta['path'].startswith('/sq/'):  # one tab strip is the only navigation between SQ pages
        strip = '<nav class="sq-tabs" aria-label="SQ5 sections">' + ''.join(
            f'<a href="{h}"{" aria-current=\"page\"" if h == meta["path"] else ""}>{t}</a>' for h, t in SQ_TABS) + '</nav>'
        body = body.replace('</section>', '</section>' + strip, 1)
    # No page ends in a dead end. Every SQ tab hands the reader the next tab (the last one goes back to
    # Projects), and every field note ends at the index. A page that writes its own Next row keeps it.
    if 'class="nextnav"' not in body:
        nxt = None
        if meta['path'].startswith('/sq/'):
            paths = [h for h, _ in SQ_TABS]
            i = paths.index(meta['path']) + 1 if meta['path'] in paths else len(paths)
            nxt = (SQ_TABS[i][0], 'Next &mdash; SQ', SQ_TABS[i][1]) if i < len(paths) else ('/projects/', 'Next &mdash; 02', 'Projects')
        elif meta['path'].startswith('/writing/') and meta.get('note'):
            nxt = ('/writing/', 'Next &mdash; 04', 'All write-ups')
        if nxt:
            row = f'<a class="nextnav" href="{nxt[0]}"><span class="eyebrow">{nxt[1]}</span><span>{nxt[2]} &rarr;</span></a>\n'
            cut = body.rindex('</main>')
            body = body[:cut] + row + body[cut:]
    if 'id="main"' not in body:
        body = body.replace('<main ', '<main id="main" ', 1)
    if meta['path'] != '/':  # home is the one page that is not an inner page
        body = body.replace('<main id="main" class="wrap', '<main id="main" class="wrap inner-page')
    if meta['path'].startswith('/writing/') and '<time datetime=' in body and 'class="byline"' not in body:
        body = body.replace('</h1>', '</h1><p class="byline">By <a href="/about.html">Amir Khademi</a></p>', 1)
    out = chrome(meta['title'], meta.get('description', ''), meta['path'], body, meta.get('nav', meta['path']), ('<meta name="robots" content="noindex,nofollow">\n' if meta.get('noindex') else '') + jsonld(meta, body))
    dest = meta['path'].lstrip('/') or 'index.html'
    if dest.endswith('/'): dest += 'index.html'
    os.makedirs(os.path.dirname(dest) or '.', exist_ok=True); open(dest, 'w').write(bust(out)); pages.append(meta['path'])
def rfc822(d):
    try: return datetime.datetime.fromisoformat(d).replace(tzinfo=datetime.timezone.utc).strftime('%a, %d %b %Y 00:00:00 +0000')
    except ValueError: return ''
feed_items = ''.join(f'<item><title>{html.escape(e["meta"]["title"])}</title><link>https://ahk02x.dev{e["meta"]["path"]}</link><guid isPermaLink="true">https://ahk02x.dev{e["meta"]["path"]}</guid>'
                     + (f'<pubDate>{rfc822(e["date"])}</pubDate>' if e['date'] else '') + f'<description>{html.escape(e["meta"].get("description", ""))}</description></item>\n' for e in posts)
open('feed.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel><title>ahk02x — field notes</title><link>https://ahk02x.dev/</link><atom:link href="https://ahk02x.dev/feed.xml" rel="self" type="application/rss+xml"/><description>Engineering write-ups by Amir Khademi: car telemetry, home infrastructure, and tools that have to earn your trust.</description><language>en</language>\n' + feed_items + '</channel></rss>\n')
open('sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>https://ahk02x.dev{p}</loc></url>\n' for p in pages if not p.startswith('/404') and p not in hidden) + '</urlset>\n')
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
public_files += [p for p in glob.glob('assets/*') + glob.glob('assets/fonts/*') + glob.glob('assets/sq-gallery/*') + glob.glob('assets/infra/*') + glob.glob('assets/about/*') + glob.glob('assets/fleet-patch/*') if os.path.isfile(p)]
public_files += [p for p in glob.glob('*.txt') if re.fullmatch(r'[0-9a-f]{32}\.txt', p)]  # IndexNow key, see tools/indexnow.py
for source in public_files:
    if os.path.exists(source):
        dest = os.path.join(public_root, source)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(source, dest)
