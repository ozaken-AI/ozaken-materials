"""Regression checks for a content-frozen, archive-wide design migration."""
import unittest
import apply_body


PAGE = '''<!doctype html><html lang="ja"><head><title>資料</title>
<style>/* unrelated style block */ .label{color:red}</style>
</head><body><section class="hero"><h1>表紙、変更しない。</h1></section>
<section class="sec-navy" data-figdark><div class="inner" data-reveal>
<h2>本文、句読点もそのまま。</h2><p>1,300人 &amp; 51施策</p>
<div class="figure"><svg viewBox="0 0 720 400"><text class="a-fade"
transform="rotate(-90 24 180)" x="24" y="180">発生頻度・件数</text>
<path class="a-flow" d="M24 180 H700"/><text>元の図の注釈</text></svg></div>
<a href="https://example.com/source?a=1&amp;b=2">出典</a></div></section>
<script>const example = ' data-oz-page="example"'; const command = 'pr';</script>
<script>
/* パーティクル・ネットワーク背景：旧背景 */
(function(){ const original = true; })();</script>
</body></html>'''


class ContentFrozenBody(unittest.TestCase):
    def test_complete_original_recovered(self):
        new = apply_body.patch(PAGE)
        self.assertEqual(apply_body.strip(new), PAGE)
        apply_body.validate(PAGE, new)
        self.assertEqual(apply_body.patch(new), new)

    def test_examples_and_positioning_attributes_are_not_owned(self):
        new = apply_body.patch(PAGE)
        self.assertIn("const example = ' data-oz-page=\"example\"';", new)
        self.assertIn('transform="rotate(-90 24 180)" x="24" y="180"', new)
        self.assertIn('表紙、変更しない。', new)
        self.assertIn(apply_body.GUARD, new)

    def test_changes_to_facts_sources_and_geometry_are_rejected(self):
        new = apply_body.patch(PAGE)
        for old, replacement in [('1,300人','1,400人'),('a=1&amp;b=2','a=2'),
                                 ('rotate(-90 24 180)','rotate(-90 30 180)'),
                                 ("const command = 'pr'", "const command = 'en'")]:
            with self.subTest(old=old), self.assertRaises(AssertionError):
                apply_body.validate(PAGE, new.replace(old, replacement))

    def test_owned_refresh_keeps_adjacent_blocks(self):
        first = apply_body.patch(PAGE)
        second = apply_body.patch(first.replace('OZ-LECTURE-BODY v1', 'OZ-LECTURE-BODY old'))
        self.assertEqual(second, first)
        self.assertIn('/* unrelated style block */', second)

    def test_approved_pilot_and_catalogue_are_distinguished(self):
        pilot = apply_body.patch(PAGE.replace('<body>', '<body class="delegation-pilot">'))
        self.assertIn('data-oz-layout="pilot"', pilot)
        self.assertNotIn('@page', apply_body.STYLE.search(pilot)[0])
        catalogue = '<html><body class="tl-body"><section class="tl-hero"></section></body></html>'
        self.assertEqual(apply_body.patch(catalogue), catalogue)


if __name__ == '__main__':
    unittest.main()
