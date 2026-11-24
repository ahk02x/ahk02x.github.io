"""The live site sends `script-src 'self'` (Cloudflare header), so the browser refuses every inline
script. A page that ships one works in a local preview and silently breaks live, as the SQ hero
animation did on 11-23. Every script on a published page must load from a file."""
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = re.compile(r'<script\b([^>]*)>(.*?)</script>', re.S | re.I)


class NoInlineScripts(unittest.TestCase):
    def test_published_pages_load_scripts_from_files_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            site = Path(tmp) / 'site'
            shutil.copytree(ROOT, site, ignore=shutil.ignore_patterns('.git', '_site', '__pycache__', 'previews'))
            subprocess.run([sys.executable, 'tools/build.py'], cwd=site, check=True, capture_output=True)
            pages = sorted((site / '_site').rglob('*.html'))
            self.assertGreater(len(pages), 10)
            bad = []
            for page in pages:
                for attrs, body in SCRIPT.findall(page.read_text(errors='replace')):
                    if body.strip() and 'application/ld+json' not in attrs:
                        bad.append(f"{page.relative_to(site / '_site')}: inline <script{attrs}> ({len(body)} bytes)")
            self.assertEqual(bad, [], "inline scripts are blocked by the live CSP; move them to /assets/*.js")


if __name__ == '__main__':
    unittest.main()
