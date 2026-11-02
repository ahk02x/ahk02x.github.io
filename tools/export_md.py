#!/usr/bin/env python3
"""Export a src/pages write-up to Markdown with dev.to front matter and a canonical link back to ahk02x.dev.
Usage: python3 tools/export_md.py src/pages/<name>.html > crosspost/<name>.md
The result is a draft (published: false): read it once on dev.to before publishing."""
import html, re, sys
SITE = 'https://ahk02x.dev'
TAGS = {'claude-code-on-call': 'devops, ai, homelab, observability', 'fleet-patch': 'devops, linux, homelab, automation',
        'lanwatch': 'networking, homelab, monitoring, python', 'memory-as-infrastructure': 'ai, devops, productivity, tooling',
        'partswatch': 'python, automation, cars, webdev', 'phosphor-wall': 'homelab, monitoring, raspberrypi, devops',
        'sq-build-log': 'cars, hardware, raspberrypi, data'}
raw = open(sys.argv[1]).read(); fm, body = raw.split('\n---\n', 1)
meta = dict(re.findall(r'^(\w+):\s*(.*)$', fm, re.M)); slug = meta['path'].rsplit('/', 1)[-1].replace('.html', '')
b = body
b = re.sub(r'<div class="eyebrow">.*?</div>', '', b, flags=re.S)
b = re.sub(r'<h1>.*?</h1>', '', b, flags=re.S)
b = re.sub(r'<p class="byline">.*?</p>', '', b, flags=re.S)
b = re.sub(r'<pre><code[^>]*>(.*?)</code></pre>', lambda m: '\n```\n' + html.unescape(m.group(1)).strip('\n') + '\n```\n', b, flags=re.S)
b = re.sub(r'<code>(.*?)</code>', lambda m: '`' + html.unescape(m.group(1)) + '`', b, flags=re.S)
b = re.sub(r'<(strong|b)>(.*?)</\1>', r'**\2**', b, flags=re.S)
b = re.sub(r'<(em|i)>(.*?)</\1>', r'*\2*', b, flags=re.S)
def link(m):
    href = m.group(1); href = SITE + href if href.startswith('/') else href
    return f'[{m.group(2)}]({href})'
b = re.sub(r'<a [^>]*href="([^"]+)"[^>]*>(.*?)</a>', link, b, flags=re.S)
b = re.sub(r'<time[^>]*>(.*?)</time>', r'\1', b, flags=re.S)
b = re.sub(r'<h2[^>]*>(.*?)</h2>', r'\n## \1\n', b, flags=re.S)
b = re.sub(r'<h3[^>]*>(.*?)</h3>', r'\n### \1\n', b, flags=re.S)
b = re.sub(r'<blockquote>(.*?)</blockquote>', lambda m: '\n> ' + re.sub(r'\s+', ' ', m.group(1)).strip() + '\n', b, flags=re.S)
b = re.sub(r'<figcaption>(.*?)</figcaption>', r'\n*\1*\n', b, flags=re.S)
def ol(m): return '\n' + '\n'.join(f'{i+1}. ' + re.sub(r'\s+', ' ', x).strip() for i, x in enumerate(re.findall(r'<li[^>]*>(.*?)</li>', m.group(1), re.S))) + '\n'
def ul(m): return '\n' + '\n'.join('- ' + re.sub(r'\s+', ' ', x).strip() for x in re.findall(r'<li[^>]*>(.*?)</li>', m.group(1), re.S)) + '\n'
b = re.sub(r'<ol[^>]*>(.*?)</ol>', ol, b, flags=re.S)
b = re.sub(r'<ul[^>]*>(.*?)</ul>', ul, b, flags=re.S)
b = re.sub(r'<p[^>]*>(.*?)</p>', lambda m: '\n' + re.sub(r'\s+', ' ', m.group(1)).strip() + '\n', b, flags=re.S)
b = re.sub(r'<(th|td)[^>]*>(.*?)</\1>', r' \2 |', b, flags=re.S); b = re.sub(r'<tr[^>]*>', '\n|', b); b = re.sub(r'</tr>', '', b)
b = re.sub(r'<[^>]+>', '', b)           # anything left (main, section, div, span, figure, table shells)
b = html.unescape(b); b = re.sub(r'[ \t]+\n', '\n', b); b = re.sub(r'\n{3,}', '\n\n', b).strip()
url = f"{SITE}{meta['path']}"
print(f'''---
title: "{meta['title'].replace('"', "'")}"
published: false
description: "{meta.get('description', '').replace('"', "'")}"
tags: {TAGS.get(slug, 'devops, homelab, ai')}
canonical_url: {url}
---

{b}

---

*Originally published at [ahk02x.dev]({url}). I'm Amir Khademi, a Site Reliability Engineer; more field notes at [ahk02x.dev/writing](https://ahk02x.dev/writing/).*
''')
