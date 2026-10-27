#!/usr/bin/env python3
"""Assemble the site: src/pages/*.html (front matter + body) -> root. Shared chrome, data-driven readouts, sitemap."""
import os, re, json, glob, html, datetime
ROOT = os.path.join(os.path.dirname(__file__), '..'); os.chdir(ROOT)
tok = json.load(open('data/tokens.json')) if os.path.exists('data/tokens.json') else {}
hc = json.load(open('sq/health.json')) if os.path.exists('sq/health.json') else {}
STATUS = {'OK': ('Healthy', 'ok'), 'WATCH': ('Keep an eye on it', 'warn'), 'FLAG': ('Needs attention', 'crit')}
word, cls = STATUS.get(hc.get('status', 'OK'), ('Healthy', 'ok'))
NAV = [('/', 'Home'), ('/projects/', 'Projects'), ('/sq/', 'SQ5 garage'), ('/writing/', 'Writing'), ('/about.html', 'About')]
MARK = '<svg viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round"><circle cx="64" cy="64" r="46"/><path d="M36,82 H54 C64,82 64,46 74,46 H92"/><path d="M36,46 H54 C64,46 64,82 74,82 H92"/></g></svg>'
GLYPHS = {
 'cross': '<svg class="glyph" viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round"><circle cx="64" cy="64" r="46"/><path d="M36,82 H54 C64,82 64,46 74,46 H92"/><path d="M36,46 H54 C64,46 64,82 74,82 H92"/></g></svg>',
 'tap': '<svg class="glyph" viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round"><path d="M20,30 H108"/><path d="M20,54 H108"/><path d="M64,54 V98"/></g></svg>',
 'node': '<svg class="glyph" viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="11" stroke-linecap="square" stroke-linejoin="miter"><path d="M66,20 V108"/><path d="M22,108 L66,20"/><path d="M33,86 H66"/><path d="M66,68 L106,28"/><path d="M66,68 L106,108"/></g></svg>',
 'wall': '<svg class="glyph" viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"><rect x="34" y="16" width="60" height="96" rx="6"/><path d="M48,40 H80"/><path d="M48,58 H80"/><path d="M48,76 H66"/></g></svg>',
 'ledger': '<svg class="glyph" viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"><path d="M24,36 H104"/><path d="M24,64 H104"/><path d="M24,92 H72"/><path d="M84,92 l8,8 l16,-18"/></g></svg>',
 'patch': '<svg class="glyph" viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"><path d="M64,20 A44,44 0 1 1 20,64"/><path d="M64,20 L48,30 L64,42"/><path d="M44,66 l12,12 l28,-30"/></g></svg>',
 'tag': '<svg class="glyph" viewBox="0 0 128 128" aria-hidden="true"><g fill="none" stroke="currentColor" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"><path d="M22,22 H66 L106,62 L62,106 L22,66 Z"/><circle cx="44" cy="44" r="7"/></g></svg>',
 'sq': '<picture><source media="(prefers-color-scheme: light)" srcset="/assets/sq-mark-light.svg"><img class="glyph sq" src="/assets/sq-mark-dark.svg" alt="" width="34" height="34"></picture>',
}
def chrome(title, desc, path, body, nav_key):
    nav = ''.join(f'<a href="{h}"{" aria-current=\"page\"" if h == nav_key else ""}>{t}</a>' for h, t in NAV)
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
<link rel="canonical" href="https://ahk02x.dev{path}">
<link rel="icon" href="/assets/mark.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="/style.css">
</head>
<body>
<header class="top"><div class="wrap"><a class="brand" href="/">{MARK}<span class="word">ahk02x<span> / Amir Khademi</span></span></a><nav class="main" aria-label="Site">{nav}</nav></div></header>
{body}
<footer><div class="wrap"><span class="word">ahk02x</span><span>Amir Khademi · Toronto, Canada</span><span><a href="mailto:amir@ahk02x.com">amir@ahk02x.com</a></span><span><a href="https://github.com/ahk02x">GitHub</a></span></div></footer>
</body>
</html>'''
def token_card():
    if not tok: return ''
    k = tok['by_kind']; tot = tok['total_tokens']
    pub = {'sq-garage': 'SQ5 garage', 'Sq': 'SQ platform', 'iot': 'IoT', 'flowtrace': 'flowtrace', 'phosphor': 'PHOSPHOR wall', 'Crucix': 'Crucix', 'alertboard': 'Alert board', 'macwatch': 'macwatch', 'netdash': 'netdash', 'partswatch': 'partswatch', 'fleet-patch': 'fleet-patch', 'lanwatch': 'lanwatch', 'inbox': 'Inbox hub', 'jackal-protocol-re': 'jackal-protocol-re'}
    shares = [(pub[p['project']], p['tokens']) for p in tok['top_projects'] if p['project'] in pub]
    rest = tot - sum(t for _, t in shares); shares.append(('Private projects', rest)); mx = max(t for _, t in shares)
    bars = ''.join(f'<div>{html.escape(n)}</div><div class="b"><i style="width:{100*t/mx:.1f}%"></i></div><div class="n">{t/1e9:.2f} B</div>' for n, t in shares)
    first = (tok.get('first') or '')[:10]
    return f'''<section id="built" class="card" style="margin-top:28px"><div class="head">{GLYPHS["ledger"]}<h3>Built with Claude Code</h3></div>
<p>Everything on this site, and everything it describes, was built in conversation with Claude Code. Every transcript on this Mac since {first}, deduplicated:</p>
<div class="tiles"><div class="tile"><div class="k">Tokens</div><div class="v">{tot/1e9:.2f}<small>billion</small></div></div><div class="tile"><div class="k">Sessions</div><div class="v">{tok["sessions"]:,}</div></div><div class="tile"><div class="k">Replies</div><div class="v">{tok["assistant_messages"]:,}</div></div><div class="tile"><div class="k">Cache reads</div><div class="v">{k.get("cache_read_input_tokens",0)/1e9:.2f}<small>billion</small></div><div class="t">fresh input {(k.get("input_tokens",0)+k.get("cache_creation_input_tokens",0))/1e6:,.0f} M · output {k.get("output_tokens",0)/1e6:,.0f} M</div></div></div>
<div class="bars">{bars}</div>
<p class="muted" style="margin-top:12px;font-size:.86rem">Counted by <a href="https://github.com/ahk02x/ahk02x.github.io/blob/main/tools/tokens.py">tools/tokens.py</a>. Streamed messages are deduplicated; a session's tokens are split evenly across the project folders it touched. Private projects are summed, never named.</p></section>'''
subs = {'{{tokens_b}}': f"{tok.get('total_tokens',0)/1e9:.2f}" if tok else '—', '{{sessions}}': f"{tok.get('sessions',0):,}" if tok else '—',
        '{{sq_word}}': word, '{{sq_cls}}': cls, '{{sq_window}}': ' to '.join(hc.get('window', ['', ''])), '{{token_card}}': token_card(),
        '{{tokens_since}}': (tok.get('first') or '')[:7]}
for g, svg in GLYPHS.items(): subs['{{glyph:' + g + '}}'] = svg
pages = []
for src in sorted(glob.glob('src/pages/*.html')):
    raw = open(src).read(); fm, body = raw.split('\n---\n', 1)
    meta = dict(re.findall(r'^(\w+):\s*(.*)$', fm, re.M))
    for a, b in subs.items(): body = body.replace(a, b)
    out = chrome(meta['title'], meta.get('description', ''), meta['path'], body, meta.get('nav', meta['path']))
    dest = meta['path'].lstrip('/') or 'index.html'
    if dest.endswith('/'): dest += 'index.html'
    os.makedirs(os.path.dirname(dest) or '.', exist_ok=True); open(dest, 'w').write(out); pages.append(meta['path'])
today = datetime.date.today().isoformat()
open('sitemap.xml', 'w').write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + ''.join(f'<url><loc>https://ahk02x.dev{p}</loc><lastmod>{today}</lastmod></url>\n' for p in pages if not p.startswith('/404')) + '</urlset>\n')
print('built', len(pages), 'pages:', ' '.join(pages))
