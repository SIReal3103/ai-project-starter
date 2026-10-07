"""Check that portability validation catches real packaging mistakes."""

from contextlib import redirect_stderr, redirect_stdout
import importlib.util
from io import StringIO
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parents[1] / 'scripts' / 'check_repository.py'
SPEC = importlib.util.spec_from_file_location('repository_checks', MODULE_PATH)
CHECKS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKS)


class RepositoryChecksTests(unittest.TestCase):
    def run_check(self, root):
        output = StringIO()
        with redirect_stdout(output), redirect_stderr(output):
            status = CHECKS.check(root)
        return status, output.getvalue()

    def test_relative_links_and_optional_fenced_examples(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'guide.md').write_text('# Guide', encoding='utf-8')
            (root / 'README.md').write_text(
                '[Guide](guide.md)\n```md\n[Future](future.md)\n```', encoding='utf-8')
            self.assertEqual(self.run_check(root)[0], 0)

    def test_missing_and_external_links_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'README.md').write_text(
                '[Missing](missing.md)\n[External](../outside.md)', encoding='utf-8')
            status, output = self.run_check(root)
            self.assertEqual(status, 1)
            self.assertIn('missing link', output)
            self.assertIn('link escapes repo', output)

    def test_machine_paths_and_invalid_python_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'guide.md').write_text('/' + 'Users/example/private-data.csv', encoding='utf-8')
            (root / 'broken.py').write_text('def broken(', encoding='utf-8')
            status, output = self.run_check(root)
            self.assertEqual(status, 1)
            self.assertIn('hardcoded machine path', output)
            self.assertIn('syntax', output)

    def test_external_directory_symlink_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            root = parent / 'repo'
            outside = parent / 'outside'
            root.mkdir()
            outside.mkdir()
            try:
                (root / 'external-docs').symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest('Creating symlinks requires privileges on this system')
            status, output = self.run_check(root)
            self.assertEqual(status, 1)
            self.assertIn('symlink depends on an external', output)

    def test_templates_are_checked_without_requiring_generated_links(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            template = root / 'templates'
            template.mkdir()
            (template / 'README.md').write_text('[Generated](future.md)', encoding='utf-8')
            self.assertEqual(self.run_check(root)[0], 0)
            (template / 'broken.py').write_text('def broken(', encoding='utf-8')
            self.assertEqual(self.run_check(root)[0], 1)


if __name__ == '__main__':
    unittest.main()
