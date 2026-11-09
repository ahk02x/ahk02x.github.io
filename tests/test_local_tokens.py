import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'tools'))
import local_tokens as lt  # noqa: E402

ORIGINAL = {"total_tokens": 11400000, "input_tokens": 8110000, "output_tokens": 3290000, "requests": 9546,
            "source": "ollama journal on the GPU host", "updated": "2026-11-02"}
STAGED = {"format": "3080-usage-totals-v1", "snapshot": "2026-11-09T04-52-39Z-8321c4cf", "date": "2026-11-09",
          "requests": 13, "completed_requests": 13, "requests_missing_complete_counters": 0,
          "input_tokens": 26897, "output_tokens": 3842}


class LocalTokens(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.out = self.dir / 'local_tokens.json'
        self.out.write_text(json.dumps(ORIGINAL))
        self.staged = self.dir / 'usage-totals.json'

    def run_with(self, staged):
        if staged is None:
            self.staged.unlink(missing_ok=True)
        else:
            self.staged.write_text(staged if isinstance(staged, str) else json.dumps(staged))
        lt.OUT, lt.CHAT_TOTALS = self.out, self.staged
        lt.main()
        return json.loads(self.out.read_text())

    def test_original_file_becomes_the_lab_source_and_chat_adds_on(self):
        d = self.run_with(STAGED)
        self.assertEqual(d['sources']['lab']['total_tokens'], 11400000)
        self.assertEqual(d['sources']['chat']['total_tokens'], 26897 + 3842)
        self.assertEqual(d['total_tokens'], 11400000 + 26897 + 3842)
        self.assertEqual(d['requests'], 9546 + 13)
        self.assertEqual(d['updated'], '2026-11-09')

    def test_nothing_private_or_finer_than_a_day_is_written(self):
        text = json.dumps(self.run_with(STAGED))
        self.assertNotIn('04-52-39', text)        # snapshot stamp carries a time of day
        self.assertNotIn('qwen', text.lower())    # never a model family name
        self.assertNotIn('192.168', text)

    def test_missing_or_malformed_staged_file_keeps_committed_numbers(self):
        first = self.run_with(STAGED)
        self.assertEqual(self.run_with(None), first)
        self.assertEqual(self.run_with('{not json'), first)
        self.assertEqual(self.run_with({**STAGED, 'input_tokens': 'lots'}), first)
        self.assertEqual(self.run_with({**STAGED, 'output_tokens': -5}), first)

    def test_counters_never_move_backwards(self):
        first = self.run_with(STAGED)
        self.assertEqual(self.run_with({**STAGED, 'input_tokens': 100}), first)

    def test_growth_is_picked_up(self):
        self.run_with(STAGED)
        d = self.run_with({**STAGED, 'input_tokens': 30000, 'requests': 15, 'date': '2026-11-10'})
        self.assertEqual(d['sources']['chat']['total_tokens'], 30000 + 3842)
        self.assertEqual(d['total_tokens'], 11400000 + 30000 + 3842)
        self.assertEqual(d['updated'], '2026-11-10')


if __name__ == '__main__':
    unittest.main()
