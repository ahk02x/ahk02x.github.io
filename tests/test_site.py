"""Regression checks for the public export and incomplete telemetry reports."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
# Deliberately synthetic input. Never used to build the committed health snapshot.
SAMPLE = {
    'status': 'OK', 'generated': '2026-10-27', 'window': ['Oct 20', 'Oct 27'],
    'week': {'oil_max': 100, 'atf_max': 90, 'knock_min': -2, 'cold_boost_s': 1,
             'boost_s': 10, 'trips': 2, 'km': 20, 'engine_h': 1, 'cold_starts': 1},
    'misfire': {'all6': 2, 'ratio': [0.5, 0.7, 1.7, 1.2, 0.8, 1.3]},
    'misfire_prior': {'all6': 2}, 'findings': [],
}

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs, self.ids = [], set()
        self.main_count = self.h1_count = 0
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'): self.ids.add(attrs['id'])
        self.main_count += tag == 'main'
        self.h1_count += tag == 'h1'
        for key in ('href', 'src'):
            if attrs.get(key): self.refs.append(attrs[key])

class SiteChecks(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.site = Path(self.tmp.name) / 'site'
        shutil.copytree(ROOT, self.site, ignore=shutil.ignore_patterns('.git', '_site', '.openai', '__pycache__', 'previews'))
    def run_script(self, name, payload=None):
        result = subprocess.run(['python3', f'tools/{name}'], cwd=self.site,
                                input=json.dumps(payload) if payload is not None else None,
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
    def health(self, data):
        self.run_script('sq_health_card.py', data)
        return (self.site/'src/pages/sq-health.html').read_text()
    def test_empty_input_is_unknown_not_healthy_or_overheated(self):
        page = self.health({})
        self.assertIn('No data / incomplete report', page)
        self.assertNotIn('Nothing unusual this week', page)
        self.assertNotIn('too hot', page)
        self.assertNotIn('a lot of timing pulled', page)
        self.assertIn('no reading available', page)
        self.assertEqual(json.loads((self.site/'sq/health.json').read_text())['status'], 'UNKNOWN')
    def test_partial_nonfinite_and_undated_reports_are_unknown(self):
        for field, value in [('oil_max', None), ('atf_max', float('nan')), ('knock_min', float('inf'))]:
            with self.subTest(field=field):
                data = copy.deepcopy(SAMPLE); data['week'][field] = value
                self.assertIn('No data / incomplete report', self.health(data))
        data = copy.deepcopy(SAMPLE); data['generated'] = 'not-a-date'
        self.assertIn('No data / incomplete report', self.health(data))
    def test_unknown_status_does_not_default_to_healthy(self):
        data = copy.deepcopy(SAMPLE); data['status'] = 'UNRECOGNIZED'
        self.assertIn('No data / incomplete report', self.health(data))
    def test_valid_report_and_accessible_exact_cylinder_values(self):
        page = self.health(copy.deepcopy(SAMPLE))
        self.assertIn('Healthy', page)
        self.assertIn('Nothing unusual this week', page)
        self.assertEqual(page.count('<th scope="row">Cylinder'), 6)
        self.assertIn('1.70×', page)
        self.assertIn('data-stale-notice', page)
    def test_zero_and_missing_previous_rate_do_not_claim_improvement(self):
        for prior in (0, None):
            data = copy.deepcopy(SAMPLE); data['misfire_prior']['all6'] = prior
            page = self.health(data)
            self.assertIn('no comparable prior rate', page)
            self.assertNotIn('down on last week', page)
    def test_exact_temperature_and_knock_thresholds(self):
        data = copy.deepcopy(SAMPLE)
        data['status'] = 'FLAG'
        data['week'].update(oil_max=130, atf_max=110, knock_min=-6)
        page = self.health(data)
        for text in ('at or above 130 °C threshold', 'at or above 110 °C threshold', 'at or beyond −6° threshold'):
            self.assertIn(text, page)
    def test_missing_health_file_and_unknown_status_on_home(self):
        (self.site/'sq/health.json').unlink()
        self.run_script('build.py')
        page = (self.site/'index.html').read_text()
        self.assertIn('No dated snapshot', page)
        self.assertNotIn('>Healthy<', page)
        (self.site/'sq/health.json').write_text(json.dumps({'status':'BAD', 'generated':'2026-10-27'}))
        self.run_script('build.py')
        self.assertIn('>No data<', (self.site/'index.html').read_text())
    def test_public_export_filters_private_names_without_changing_totals(self):
        path = self.site/'data/tokens.json'; data=json.loads(path.read_text())
        totals = data['total_tokens']; kinds = data['by_kind'].copy()
        data['top_projects'].append({'project':'PRIVATE_SENTINEL', 'tokens':12})
        data['first']='2026-07-04T21:16:16Z'; data['last']='2026-10-27T18:45:22Z'
        data['extra_private_field']='PRIVATE_SENTINEL'
        path.write_text(json.dumps(data)); self.run_script('build.py')
        for target in (path, self.site/'_site/data/tokens.json'):
            clean=json.loads(target.read_text())
            self.assertNotIn('PRIVATE_SENTINEL', target.read_text())
            self.assertEqual(clean['first'],'2026-07'); self.assertEqual(clean['last'],'2026-10')
            self.assertEqual(clean['total_tokens'],totals); self.assertEqual(clean['by_kind'],kinds)
    def test_source_trailing_newlines_do_not_change_generated_pages(self):
        self.run_script('build.py')
        before = (self.site/'about.html').read_bytes()
        source = self.site/'src/pages/about.html'
        source.write_text(source.read_text().rstrip() + '\n\n\n')
        self.run_script('build.py')
        self.assertEqual(before, (self.site/'about.html').read_bytes())
    def test_public_build_links_landmarks_and_packaging(self):
        self.run_script('build.py'); public=self.site/'_site'
        pages={}
        for path in public.rglob('*.html'):
            page=Page(); text=path.read_text(); page.feed(text); pages[path]=page
            self.assertNotIn('{{', text)
            self.assertEqual(page.main_count,1,str(path)); self.assertEqual(page.h1_count,1,str(path))
            self.assertIn('main',page.ids)
        self.assertEqual(len(pages),8)
        for path,page in pages.items():
            for ref in page.refs:
                u=urlsplit(ref)
                if u.scheme or u.netloc: continue
                dest=public/u.path.lstrip('/') if u.path.startswith('/') else path.parent/u.path if u.path else path
                if dest.is_dir():dest=dest/'index.html'
                self.assertTrue(dest.exists(),f'{path}: {ref}')
                if u.fragment and dest in pages:self.assertIn(unquote(u.fragment),pages[dest].ids)
        for excluded in ('tools','src','tests','publish.sh','HANDOFF.md','.git','docs','qa.html'):
            self.assertFalse((public/excluded).exists(),excluded)
        before={str(p.relative_to(public)):p.read_bytes() for p in public.rglob('*') if p.is_file()}
        self.run_script('build.py')
        after={str(p.relative_to(public)):p.read_bytes() for p in public.rglob('*') if p.is_file()}
        self.assertEqual(before,after)

if __name__ == '__main__': unittest.main()
