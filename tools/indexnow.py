#!/usr/bin/env python3
"""Tell the IndexNow engines (Bing, and through it DuckDuckGo; Yandex, Naver, Seznam) which URLs changed.

Reads sitemap.xml and the <key>.txt file at the site root (the key is public by design; the engine fetches
that file to prove the submitter controls the host). No account needed. CI runs this after each push to
main; run it by hand after any out-of-band change:  python3 tools/indexnow.py [url ...]
"""
import glob, json, os, re, sys, urllib.error, urllib.request
import xml.etree.ElementTree as ET
ROOT = os.path.join(os.path.dirname(__file__), '..'); os.chdir(ROOT)
keys = [p for p in glob.glob('*.txt') if re.fullmatch(r'[0-9a-f]{32}\.txt', p)]
if len(keys) != 1: sys.exit(f'expected exactly one 32-hex key file at the site root, found {keys}')
key = keys[0][:-4]
NS = '{http://www.sitemaps.org/schemas/sitemap/0.9}'
urls = sys.argv[1:] or [u.text for u in ET.parse('sitemap.xml').getroot().iter(NS + 'loc')]
body = json.dumps({'host': 'ahk02x.dev', 'key': key, 'keyLocation': f'https://ahk02x.dev/{key}.txt', 'urlList': urls}).encode()
req = urllib.request.Request('https://api.indexnow.org/indexnow', data=body, method='POST',
                             headers={'Content-Type': 'application/json; charset=utf-8'})
try:
    with urllib.request.urlopen(req, timeout=30) as r:
        print(f'IndexNow HTTP {r.status}: {len(urls)} URLs submitted')
except urllib.error.HTTPError as e:
    sys.exit(f'IndexNow HTTP {e.code}: {e.read().decode(errors="replace")[:300]}')
