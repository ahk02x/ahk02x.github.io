#!/usr/bin/env python3
"""Assemble the site: src/pages/*.html (front matter + body) -> root. Shared chrome, data-driven readouts, sitemap."""
import os, re, json, glob, html, datetime, shutil
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
 'sq': '<span class="sq-brand"><img class="glyph sq sq-dark" src="/assets/sq-mark-dark.svg" alt="" width="34" height="34"><img class="glyph sq sq-light" src="/assets/sq-mark-light.svg" alt="" width="34" height="34"></span>',
}
def chrome(title, desc, path, body, nav_key, extra_head=''):
    if 'Amir Khademi' not in title and title != 'Not found': title = f'{title} · Amir Khademi'  # every indexed page carries the author's name
    nav = ''.join(f'<a href="{h}"' + (' aria-current="page"' if h == nav_key else '') + f'><span class="nav-index" aria-hidden="true">{i:02}</span>{t}</a>' for i, (h, t) in enumerate(NAV))
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
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<script src="/assets/theme-init.js"></script>
<link rel="stylesheet" href="/style.css">
<script src="/assets/site.js" defer></script>
<meta name="theme-color" content="#f2f0e9">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://ahk02x.dev{path}">
{extra_head}</head>
<body>
<a class="skip-link" href="#main">Skip to content</a>
<header class="top"><div class="wrap"><a class="brand" href="/" aria-label="ahk02x — home">{MARK}<span class="word">ahk02x<span> / field notes</span></span></a><nav class="main" aria-label="Main navigation">{nav}</nav><button class="theme-toggle" type="button" aria-label="Switch to dark theme" hidden><span class="theme-icon" aria-hidden="true">◐</span><span data-theme-label>Dark</span></button></div></header>
{body}
<footer><div class="wrap"><div class="footer-heading"><span class="eyebrow">Have a question or a good problem?</span><a class="footer-contact" href="mailto:amir@ahk02x.com">Let's talk.<span aria-hidden="true">↗</span></a></div><div class="footer-meta"><span class="word">{MARK} ahk02x / Amir Khademi</span><span>Toronto, Canada · Text beats calls.</span><a href="https://github.com/ahk02x">GitHub ↗</a><a href="mailto:amir@ahk02x.com">Email ↗</a><a href="#main">Back to top ↑</a></div></div></footer>
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
    return f'''<section id="built" class="card" style="margin-top:28px"><div class="head">{GLYPHS["ledger"]}<h3>Built with Claude Code</h3></div>
<p>Claude Code has been part of the work behind these projects. Usage recorded in its transcripts since {first}, deduplicated:</p>
<div class="tiles"><div class="tile"><div class="k">Tokens</div><div class="v">{tot/1e9:.2f}<small>billion</small></div></div><div class="tile"><div class="k">Sessions</div><div class="v">{tok["sessions"]:,}</div></div><div class="tile"><div class="k">Replies</div><div class="v">{tok["assistant_messages"]:,}</div></div><div class="tile"><div class="k">Cache reads</div><div class="v">{k.get("cache_read_input_tokens",0)/1e9:.2f}<small>billion</small></div><div class="t">fresh input {(k.get("input_tokens",0)+k.get("cache_creation_input_tokens",0))/1e6:,.0f} M · output {k.get("output_tokens",0)/1e6:,.0f} M</div></div></div>
<div class="bars">{bars}</div>
<p class="muted" style="margin-top:12px;font-size:.86rem">Counted by <a href="https://github.com/ahk02x/ahk02x.github.io/blob/main/tools/tokens.py">tools/tokens.py</a>. Streamed messages are deduplicated; a session's tokens are split evenly across the project folders it touched. Private projects are summed, never named. Totals include cache reads; these are usage counters, not unique generated words or a cost estimate.</p></section>'''
subs = {'{{tokens_b}}': f"{tok.get('total_tokens',0)/1e9:.2f}" if tok else '—', '{{sessions}}': f"{tok.get('sessions',0):,}" if tok else '—',
        '{{sq_word}}': word, '{{sq_cls}}': cls, '{{sq_window}}': ' to '.join(hc.get('window', ['', ''])), '{{token_card}}': token_card(),
        '{{tokens_since}}': (tok.get('first') or '')[:7], '{{sq_generated}}': html.escape(hc.get('generated', ''))}
for g, svg in GLYPHS.items(): subs['{{glyph:' + g + '}}'] = svg
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
pages = []
for src in sorted(glob.glob('src/pages/*.html')):
    raw = open(src).read(); fm, body = raw.split('\n---\n', 1)
    body = body.strip()
    meta = dict(re.findall(r'^(\w+):\s*(.*)$', fm, re.M))
    for a, b in subs.items(): body = body.replace(a, b)
    if 'id="main"' not in body:
        body = body.replace('<main ', '<main id="main" ', 1)
    body = body.replace('<main id="main" class="wrap', '<main id="main" class="wrap inner-page')
    if meta['path'].startswith('/writing/') and '<time datetime=' in body and 'class="byline"' not in body:
        body = body.replace('</h1>', '</h1><p class="byline">By <a href="/about.html">Amir Khademi</a></p>', 1)
    out = chrome(meta['title'], meta.get('description', ''), meta['path'], body, meta.get('nav', meta['path']), jsonld(meta, body))
    dest = meta['path'].lstrip('/') or 'index.html'
    if dest.endswith('/'): dest += 'index.html'
    os.makedirs(os.path.dirname(dest) or '.', exist_ok=True); open(dest, 'w').write(out); pages.append(meta['path'])
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
public_files = ['style.css', 'robots.txt', '.well-known/security.txt', 'sitemap.xml', 'CNAME', '.nojekyll', 'data/tokens.json', 'sq/health.json']
public_files += [(p.lstrip('/') or 'index.html') + ('index.html' if p.endswith('/') and p != '/' else '') for p in pages]
public_files += [p for p in glob.glob('assets/*') if os.path.isfile(p)]
public_files += [p for p in glob.glob('*.txt') if re.fullmatch(r'[0-9a-f]{32}\.txt', p)]  # IndexNow key, see tools/indexnow.py
for source in public_files:
    if os.path.exists(source):
        dest = os.path.join(public_root, source)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copyfile(source, dest)
