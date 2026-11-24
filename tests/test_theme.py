"""The theme contract, enforced.

docs/theme.md says the look in prose; nothing checked that a page obeyed it. A page could style
itself with tokens this theme never defines, or bring its own hex colour, radius or shadow, and
every existing test still passed: they read structure, never style. That is how the Trends page
kept a circular glowing photo, parked over its own lede, through a whole theme rebuild.

These checks are text-only and need no browser:

1. Every CSS custom property a page reads must be defined somewhere. An undefined token is the
   signature of a page that was skipped: its rules silently fall back to nothing.
2. No page brings its own colour. Hex and rgb() literals belong to the palette in style.css and to
   the few places that draw a physical object (the logger box's real wire colours), which say so.
3. No radius, no shadow. The theme has no rounded surfaces; the exceptions are the handful of
   genuinely circular marks, which must be exactly round (50% or 999px) and small.
4. An absolutely positioned element inside a page's own styles must say what keeps it off the text.
"""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted((ROOT / 'src' / 'pages').glob('*.html'))
STYLE = (ROOT / 'style.css').read_text()

# Tokens the browser or the chrome provides, not the page.
BUILTIN = {'--mono', '--sans'}
# Pages that draw a physical object may name its real colours, and say so in a comment.
OBJECT_COLOUR_PAGES = {'sq-logger.html'}


def declared(text):
    return set(re.findall(r'(--[a-zA-Z0-9-]+)\s*:', text))


def used(text):
    """Tokens read with no fallback. var(--x, 2) carries its own default and cannot fall through."""
    return {m.group(1) for m in re.finditer(r'var\(\s*(--[a-zA-Z0-9-]+)\s*([,)])', text) if m.group(2) == ')'}


def styles_of(page_text):
    """Only what the page itself styles: its <style> blocks and any style= attributes."""
    return '\n'.join(re.findall(r'<style>(.*?)</style>', page_text, re.S)
                     + re.findall(r'style="([^"]*)"', page_text))


class ThemeContract(unittest.TestCase):
    def test_every_token_a_page_reads_is_defined(self):
        theme = declared(STYLE) | BUILTIN
        for page in PAGES:
            text = page.read_text()
            own = styles_of(text)
            undefined = sorted(used(own) - theme - declared(own))
            self.assertEqual(undefined, [], f'{page.name} reads tokens no stylesheet defines: {undefined}')

    def test_no_page_brings_its_own_colour(self):
        for page in PAGES:
            if page.name in OBJECT_COLOUR_PAGES:
                continue
            own = styles_of(page.read_text())
            literals = re.findall(r'#[0-9a-fA-F]{3,8}\b|\brgba?\([^)]*\)', own)
            self.assertEqual(literals, [], f'{page.name} hardcodes a colour: {literals}')

    def test_no_rounded_surfaces_or_shadows(self):
        for page in PAGES:
            own = styles_of(page.read_text())
            self.assertNotIn('box-shadow', own, f'{page.name} casts a shadow; the theme has none')
            for value in re.findall(r'border-radius\s*:\s*([^;}"]+)', own):
                self.assertIn(value.strip(), ('0', '50%', '999px'),
                              f'{page.name} rounds a surface ({value.strip()}); only a true circle is allowed')

    def test_no_page_floats_a_picture_over_its_own_text(self):
        """The Trends photo sat on its own lede: an <img> the page positioned absolutely.

        A picture is laid out by the grid or it is not on the page. Text that a screen reader needs
        but a reader does not (the off-screen class every page uses) is not a picture, so the rule
        is specific: no class that an <img> or <video> on this page carries may be positioned.
        """
        for page in PAGES:
            text = page.read_text()
            media = set()
            for tag in re.findall(r'<(?:img|video)\b[^>]*>', text):
                cls = re.search(r'class="([^"]*)"', tag)
                if cls:
                    media.update(cls.group(1).split())
            if not media:
                continue
            for rule in re.findall(r'([^{}]+)\{([^{}]*position\s*:\s*absolute[^{}]*)\}', styles_of(text)):
                hit = sorted(c for c in media if re.search(r'\.' + re.escape(c) + r'\b', rule[0]))
                self.assertEqual(hit, [], f'{page.name} positions a picture over the page: .{hit and hit[0]}')


if __name__ == '__main__':
    unittest.main()
