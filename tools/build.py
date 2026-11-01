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
GLYPHS = {
 'cross': '<svg class="glyph" viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round"><circle cx="64" cy="64" r="46"/><path d="M36,82 H54 C64,82 64,46 74,46 H92"/><path d="M36,46 H54 C64,46 64,82 74,82 H92"/></g></svg>',
 'tap': '<svg class="glyph" viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round"><path d="M20,30 H108"/><path d="M20,54 H108"/><path d="M64,54 V98"/></g></svg>',
 'node': '<svg class="glyph" viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="11" stroke-linecap="square" stroke-linejoin="miter"><path d="M66,20 V108"/><path d="M22,108 L66,20"/><path d="M33,86 H66"/><path d="M66,68 L106,28"/><path d="M66,68 L106,108"/></g></svg>',
 'wall': '<svg class="glyph" viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"><rect x="34" y="16" width="60" height="96" rx="6"/><path d="M48,40 H80"/><path d="M48,58 H80"/><path d="M48,76 H66"/></g></svg>',
 'ledger': '<svg class="glyph" viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"><path d="M24,36 H104"/><path d="M24,64 H104"/><path d="M24,92 H72"/><path d="M84,92 l8,8 l16,-18"/></g></svg>',
 'patch': '<svg class="glyph" viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"><path d="M64,20 A44,44 0 1 1 20,64"/><path d="M64,20 L48,30 L64,42"/><path d="M44,66 l12,12 l28,-30"/></g></svg>',
 'tag': '<svg class="glyph" viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"><path d="M22,22 H66 L106,62 L62,106 L22,66 Z"/><circle cx="44" cy="44" r="7"/></g></svg>',
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
<footer class="site-footer"><span>AHK02X / Toronto</span></footer>
</div>
</body>
</html>'''
def token_card():
    if not tok: return ''
    k = tok['by_kind']; tot = tok['total_tokens']
    pub = {'sq-garage': 'SQ5 garage', 'Sq': 'SQ platform', 'iot': 'IoT', 'flowtrace': 'flowtrace', 'phosphor': 'PHOSPHOR wall', 'Crucix': 'Crucix', 'alertboard': 'Alert board', 'macwatch': 'macwatch', 'netdash': 'netdash', 'partswatch': 'partswatch', 'fleet-patch': 'fleet-patch', 'lanwatch': 'lanwatch', 'inbox': 'Inbox hub', 'jackal-protocol-re': 'jackal-protocol-re'}
    shares = [(pub[p['project']], p['tokens']) for p in tok['top_projects'] if p['project'] in pub]
    rest = tot - sum(t for _, t in shares); shares.append(('Private projects', rest)); mx = max(t for _, t in shares)
    bars = ''.join(f'<div>{html.escape(n)}</div><div class="b"><i style="width:{100*t/mx:.1f}%"></i></div><div class="n">{t/1e9:.2f} B</div>' for n, t in shares)
    first = (tok.get('first') or '')[:7]
    months = [m for m in (tok.get('by_month') or []) if m.get('tokens')]
    month_html = ''
    if months:
        mmx = max(m['tokens'] for m in months)
        this_month = (tok.get('last') or '')[:7]
        def mlabel(ym):
            try: lbl = datetime.date(int(ym[:4]), int(ym[5:7]), 1).strftime('%b %Y')
            except ValueError: return ym
            return lbl + ' <small>so far</small>' if ym == this_month else lbl
        mbars = ''.join(f'<div>{mlabel(m["month"])}</div><div class="b"><i style="width:{100*m["tokens"]/mmx:.1f}%"></i></div><div class="n">{m["tokens"]/1e9:.2f} B</div>' for m in months)
        month_html = f'<div class="eyebrow" style="margin-top:26px">By month</div><div class="bars">{mbars}</div>'
    return f'''<section id="built" class="card" style="margin-top:28px"><div class="head">{GLYPHS["ledger"]}<h3>Built with Claude Code</h3></div>
<p>Claude Code has been part of the work behind these projects. Usage recorded in its transcripts since {first}, deduplicated:</p>
<div class="tiles"><div class="tile"><div class="k">Tokens</div><div class="v">{tot/1e9:.2f}<small>billion</small></div></div><div class="tile"><div class="k">Sessions</div><div class="v">{tok["sessions"]:,}</div></div><div class="tile"><div class="k">Replies</div><div class="v">{tok["assistant_messages"]:,}</div></div><div class="tile"><div class="k">Cache reads</div><div class="v">{k.get("cache_read_input_tokens",0)/1e9:.2f}<small>billion</small></div><div class="t">fresh input {(k.get("input_tokens",0)+k.get("cache_creation_input_tokens",0))/1e6:,.0f} M · output {k.get("output_tokens",0)/1e6:,.0f} M</div></div></div>
<div class="eyebrow" style="margin-top:26px">By project</div><div class="bars">{bars}</div>
{month_html}
<p class="muted" style="margin-top:12px;font-size:.86rem">Counted by <a href="https://github.com/ahk02x/ahk02x.github.io/blob/main/tools/tokens.py">tools/tokens.py</a>. Streamed messages are deduplicated; a session's tokens are split evenly across the project folders it touched. Private projects are summed, never named. Totals include cache reads; these are usage counters, not unique generated words or a cost estimate.</p></section>'''
gtok = json.load(open('data/gpt_tokens.json')) if os.path.exists('data/gpt_tokens.json') else {}
ghist = json.load(open('data/gpt_history.json')) if os.path.exists('data/gpt_history.json') else {}  # ChatGPT web estimate (2023 on), tools/gpt_history.py
_ct, _gt = (tok or {}).get('total_tokens', 0), gtok.get('total_tokens', 0) + ghist.get('tokens', 0); _mx = max(_ct, _gt, 1)
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
    stats = [(short(_ct + _gt), 'Lifetime tokens'), (short(max(days.values())), 'Peak day'),
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
def gh_grid():
    import datetime as dt
    g = json.load(open('data/github.json')) if os.path.exists('data/github.json') else {}
    if not g: return ''
    return grid_html(collections.Counter(g['by_day']), dt.date.fromisoformat(max(max(g['by_day']), gtok.get('updated', '0000')[:10])))
subs = {'{{claude_tokens}}': f"{_ct:,}" if _ct else '—', '{{gpt_tokens}}': f"{_gt:,}" if _gt else '—',
        '{{claude_pct}}': f"{max(_ct/_mx*100, 1 if _ct else 0):.1f}", '{{gpt_pct}}': f"{max(_gt/_mx*100, 1 if _gt else 0):.1f}",
        '{{tokens_updated}}': (gtok.get('updated', '') + ' ET') if gtok.get('updated') else '—',
        '{{gpt_note}}': f" · GPT includes ~{ghist['tokens']/1e6:,.0f}M estimated ChatGPT use since {ghist.get('since', '2023')}" if ghist.get('tokens') else '',
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
          'description': 'Site Reliability Engineer in Toronto, Canada. Writes about car telemetry, home infrastructure and agent tooling at ahk02x.dev.',
          'email': 'mailto:amir@ahk02x.com',
          'address': {'@type': 'PostalAddress', 'addressLocality': 'Toronto', 'addressRegion': 'ON', 'addressCountry': 'CA'},
          'knowsAbout': ['Site reliability engineering', 'Linux', 'Kubernetes', 'Observability', 'Home infrastructure', 'Vehicle telemetry', 'AI agent tooling'],
          'sameAs': ['https://github.com/ahk02x']}
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
        tabs = [('/sq/', 'Overview'), ('/sq/health.html', 'Weekly health'), ('/sq/build-log.html', 'Build log')]
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
public_files = ['style.css', 'robots.txt', '.well-known/security.txt', 'sitemap.xml', 'feed.xml', 'CNAME', '.nojekyll', 'data/tokens.json', 'data/gpt_tokens.json', 'data/github.json', 'sq/health.json']
public_files += [(p.lstrip('/') or 'index.html') + ('index.html' if p.endswith('/') and p != '/' else '') for p in pages]
public_files += [p for p in glob.glob('assets/*') if os.path.isfile(p)]
public_files += [p for p in glob.glob('*.txt') if re.fullmatch(r'[0-9a-f]{32}\.txt', p)]  # IndexNow key, see tools/indexnow.py
for source in public_files:
    if os.path.exists(source):
        dest = os.path.join(public_root, source)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(source, dest)
