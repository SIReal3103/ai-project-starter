"""Tests for portable skill reference generation, using only the standard library."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "sync-skills.py"
SPEC = importlib.util.spec_from_file_location("sync_skills", SCRIPT)
sync = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(sync)


class SectionTests(unittest.TestCase):
    def test_fenced_headings_do_not_end_real_section(self):
        text = "## 1 Parent\n~~~text\n## 9 Fake\n~~~\n### 1.1 Child\nx\n## 2 Next\ny\n"
        index = sync.section_index(text)
        self.assertNotIn("9", index)
        self.assertEqual(sync.excerpt(text, index, ["1.1"]), "### 1.1 Child\nx\n")
        self.assertIn("## 9 Fake", sync.excerpt(text, index, ["1"]))

    def test_parent_and_child_selection_does_not_repeat_text(self):
        text = "## 5 Product\nintro\n### C1 First\none\n### C2 Second\ntwo\n## 6 Next\n"
        index = sync.section_index(text)
        result = sync.excerpt(text, index, ["C2", "5", "C1"])
        self.assertEqual(result.count("### C1"), 1)
        self.assertEqual(result.count("### C2"), 1)
        self.assertNotIn("## 6", result)

    def test_missing_and_duplicate_section_are_errors(self):
        with self.assertRaises(ValueError):
            sync.section_index("## 1 First\n## 1 Duplicate\n")
        text = "## 1 One\n"
        with self.assertRaises(ValueError):
            sync.excerpt(text, sync.section_index(text), ["8"])


class BundleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "skills").mkdir()
        (self.root / "guide.md").write_text("## 1 Domain\nbody\n## 2 Shared\ncommon\n## 3 Plan\nsteps\n")
        self.catalog = {
            "source": "guide.md", "shared_contract_section": "2", "planning_sections": ["3"],
            "skills": [{"name": "sample-skill", "primary_sections": ["1"], "source_sections": ["1"]}],
        }
        self.write_catalog()

    def tearDown(self):
        self.temp.cleanup()

    def write_catalog(self):
        (self.root / "skills/catalog.json").write_text(json.dumps(self.catalog))

    def run_sync(self, check=False):
        with contextlib.redirect_stdout(io.StringIO()):
            return sync.synchronize(self.root, check)

    def test_missing_stale_read_only_check_and_repair(self):
        self.assertEqual(self.run_sync(True), 1)
        self.assertFalse((self.root / "skills/sample-skill").exists())
        self.assertEqual(self.run_sync(), 0)
        self.assertEqual(self.run_sync(True), 0)
        target = self.root / "skills/sample-skill/references/techstack-guide.md"
        target.write_text("local change\n")
        self.assertEqual(self.run_sync(True), 1)
        self.assertEqual(target.read_text(), "local change\n")
        self.assertEqual(self.run_sync(), 0)
        self.assertEqual(self.run_sync(True), 0)
        self.assertIn("## 1 Domain", target.read_text())
        self.assertNotIn("## 2 Shared", target.read_text())

    def test_invalid_catalog_does_not_partially_write(self):
        self.catalog["skills"].append({"name": "other-skill", "primary_sections": ["99"], "source_sections": ["99"]})
        self.write_catalog()
        with self.assertRaises(ValueError):
            self.run_sync()
        self.assertFalse((self.root / "skills/sample-skill").exists())

    def test_invalid_name_and_unknown_selection(self):
        with self.assertRaises(ValueError):
            sync.build_outputs(self.root, "not-present")
        self.catalog["skills"][0]["name"] = "../escape"
        self.write_catalog()
        with self.assertRaises(ValueError):
            self.run_sync()

    def test_source_change_invalidates_bundle(self):
        self.run_sync()
        source = self.root / "guide.md"
        source.write_text(source.read_text().replace("body", "new body"))
        self.assertEqual(self.run_sync(True), 1)
        self.run_sync()
        self.assertEqual(self.run_sync(True), 0)


if __name__ == "__main__":
    unittest.main()
