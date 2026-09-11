"""Lossless migration checks for an archive-wide encrypted update. No browser needed."""
from pathlib import Path
import tempfile
import unittest

import apply_cover as cover


def page(hero, tail='<section class="sec-light"><p>本文、注記。<a href="#detail">参照</a></p></section>'):
    return '<!doctype html><html><head><style>/* existing styles */</style></head><body>' + hero + tail + '<script>window.existingCommand = "pr";</script></body></html>'


HERO = '''<section class="hero" id="intro"><a class="oz-home" href="/index.html">戻る</a>
<div class="texture" aria-hidden="true"><svg><text>DECOR</text></svg></div><div class="inner">
<span class="eyebrow">AI &amp; Work</span><h1 class="hero-title">AIの、役割<br>「任せる」へ。</h1>
<p class="hero-copy">対象を決める。範囲を、渡す。</p>
<p class="hero-meta"><b>登壇者 A</b><span data-label="A、B。">所属</span><br>登壇者 B ／ 所属 B</p>
</div></section>'''


class CoverMigration(unittest.TestCase):
    def test_body_and_scripts_are_byte_identical(self):
        old = page(HERO)
        new = cover.patch(old)
        old_body = cover.Tree(old).root.first('sec-light').outer(old)
        self.assertIn(old_body, new)
        self.assertIn('<script>window.existingCommand = "pr";</script>', new)
        self.assertIn('id="intro"', new)

    def test_only_visible_cover_punctuation_is_removed(self):
        new = cover.patch(page(HERO))
        hero = cover.Tree(new).root.first('hero').outer(new)
        self.assertNotRegex(cover.text(hero), '[、。]')
        self.assertIn('data-label="A、B。"', hero)
        self.assertIn('対象を決める<br>範囲を渡す', hero)
        self.assertIn('AI &amp; Work', hero)
        self.assertIn('本文、注記。', new)

    def test_refresh_does_not_duplicate_or_lose_sections(self):
        first = cover.patch(page(HERO))
        self.assertEqual(first, cover.patch(first))
        self.assertEqual(first.count('id="oz-cover-style"'), 1)
        self.assertEqual(first.count('id="oz-cover-script"'), 1)

    def test_facts_and_links_move_below_cover_intact(self):
        facts = '<div class="hero-stats"><b>51</b><a href="#detail">内訳、確認。</a></div>'
        new = cover.patch(page(HERO.replace('</div></section>', facts + '</div></section>')))
        self.assertIn('<div class="oz-cover-details">' + facts + '</div>', new)
        self.assertLess(new.index('</section>'), new.index(facts))

    def test_unknown_content_stops_the_migration(self):
        with self.assertRaisesRegex(ValueError, 'Unmapped cover content'):
            cover.patch(page(HERO.replace('</div></section>', '<p>未分類の重要な注意</p></div></section>')))

    def test_poster_preserves_legend_and_board_preserves_timestamp(self):
        for heading, tail in [
            ('<div class="poster"><div class="top"><div class="top-l"><div class="eyebrow">Master</div><h1>51施策</h1><p>全体像。</p></div>', '<div class="top-r">凡例と51施策</div></div><div class="grid">全データ</div></div>'),
            ('<div class="wrap"><header class="top"><div><span class="badge">Board</span><h1>統計</h1><p class="h-sub">同じ率。</p></div>', '<div class="stamp">UPDATED 2026年8月22日</div></header><section class="panel">全データ</section></div>')]:
            new = cover.patch(page(heading + tail))
            self.assertIn(tail, new)
            self.assertEqual(new.count('<h1'), 1)
            self.assertEqual(new, cover.patch(new))

    def test_preview_cannot_overwrite_repository_through_a_link(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            repo = base / 'repo'; repo.mkdir()
            encrypted = repo / 'private.html'; encrypted.write_text('encrypted')
            preview = base / 'preview.html'; preview.symlink_to(encrypted)
            with self.assertRaises(ValueError):
                cover.safe_preview(preview, repo)
            self.assertEqual(encrypted.read_text(), 'encrypted')


if __name__ == '__main__':
    unittest.main()
