"""Catch the released state where the body was migrated but the cover was not."""
import unittest
import apply_body
import apply_cover
from check_design import issues
from test_apply_cover import page, HERO


class DesignReleaseCheck(unittest.TestCase):
    def test_body_only_migration_does_not_pass_as_complete(self):
        source = apply_body.patch(page(HERO))
        self.assertIn('common cover missing', issues(source))

    def test_complete_migration_passes(self):
        source = apply_body.patch(apply_cover.patch(page(HERO)))
        self.assertEqual(issues(source), [])

    def test_new_unstyled_section_is_detected(self):
        source = apply_body.patch(apply_cover.patch(page(HERO)))
        source = source.replace('</body>', '<section class="sec-light"><p>追加章</p></section></body>')
        self.assertIn('a content surface is outside the lecture design', issues(source))

    def test_lost_motion_script_is_detected(self):
        source = apply_body.patch(apply_cover.patch(page(HERO)))
        source = apply_cover.SCRIPT_RE.sub('', source)
        self.assertIn('oz-cover-script missing, empty or duplicated', issues(source))


if __name__ == '__main__':
    unittest.main()
