"""Exercise scaffolding in isolated source repos, including portability and safety."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import unicodedata
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
GUIDES = (
    "architecture-and-use-cases.md", "chatbot-rag-and-agents.md",
    "backend-security-and-privacy.md", "voice-and-media.md",
    "evals-and-observability.md", "two-hour-workflow.md", "provider-profiles.md",
)
EXPECTED_DOCS = (
    "project-brief.md", "acceptance-contract.md", "architecture-decisions.md",
    "implementation-plan.md", "eval-plan.md", "data-handling.md", "handoff.md",
    "stack-guide.md", "configuration.md",
)


class NewProjectTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="starter-contract-")
        self.addCleanup(self.temporary.cleanup)
        self.base = Path(self.temporary.name).resolve()
        self.source = self.base / "source starter"
        self.source.mkdir()
        (self.source / "scripts").mkdir()
        shutil.copyfile(ROOT / "scripts" / "new_project.py", self.source / "scripts" / "new_project.py")
        shutil.copytree(ROOT / "templates", self.source / "templates")
        self.script = self.source / "scripts" / "new_project.py"
        self.target = self.base / "new project"
        self.caller = self.base / "unrelated working directory"
        self.caller.mkdir()
        self.eval_source = self.source / "tools" / "evals"
        # Fixture-only eval package: it verifies file lookup after relocation, not AI quality.
        files = {
            "README.md": "# Fixture eval\n[Old demo](example-results/report.html)\n",
            "main.py": (
                "import json\nfrom pathlib import Path\n"
                "rows = [json.loads(line) for line in (Path(__file__).parent / 'datasets' / 'demo-cases.jsonl').read_text(encoding='utf-8').splitlines()]\n"
                "assert rows == [{'id': 'fixture-case'}]\n"
                "print('fixture dataset resolved independently')\n"
            ),
            "scoring.py": '"""Fixture only."""\n',
            "report.py": '"""Fixture only."""\n',
            "agent-guide.md": "# Fixture guide\n[Dataset](datasets/dataset-guide.md)\n",
            "adapters/demo.py": '"""Fixture only."""\n',
            "adapters/http-product.py": '"""Fixture only."""\n',
            "adapters/openai-chat.py": '"""Fixture only."""\n',
            "datasets/demo-cases.jsonl": json.dumps({"id": "fixture-case"}) + "\n",
            "datasets/dataset-guide.md": "# Fixture dataset guide\n",
            "integrations/README.md": "# Fixture framework guide\n",
            "templates/report-template.html": "<!doctype html><title>Fixture report</title>\n",
            "templates/case-template.json": "{}\n",
            "setup-tools.sh": "# fixture, never executed\n",
            "render-pdf.mjs": "// fixture, never executed\n",
            ".env.example": "EVAL_TARGET_API_KEY=\n",
        }
        for relative, content in files.items():
            self.write_source(relative, content)
        guide_root = self.source / "docs" / "guides"
        guide_root.mkdir(parents=True)
        for name in GUIDES:
            (guide_root / name).write_text("# Fixture guide\n[Eval kit](../../tools/evals/README.md)\n", encoding="utf-8")

    def write_source(self, relative, content):
        path = self.eval_source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def run_cli(self, *args, cwd=None, env=None):
        return subprocess.run(
            [sys.executable, "-B", str(self.script), *map(str, args)],
            cwd=cwd or self.caller,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
            check=False,
        )

    def create(self, *extra, name="Dự án thử nghiệm", target=None, **options):
        return self.run_cli("--name", name, "--destination", target or self.target, *extra, **options)

    def assert_success(self, result):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def assert_markdown_links_resolve(self, root):
        checked = 0
        for markdown in root.rglob("*.md"):
            source = markdown.read_text(encoding="utf-8")
            self.assertNotIn(str(self.source), source, str(markdown))
            for raw in re.findall(r"\[[^\]]*\]\(([^)]+)\)", source):
                target = raw.strip().strip("<>")
                parsed = urlsplit(target)
                if parsed.scheme or target.startswith("#"):
                    continue
                self.assertFalse(Path(parsed.path).is_absolute(), (markdown, target))
                linked = (markdown.parent / unquote(parsed.path)).resolve()
                self.assertTrue(linked.is_relative_to(root.resolve()), (markdown, target))
                self.assertTrue(linked.exists(), (markdown, target))
                checked += 1
        self.assertGreater(checked, 25)

    def test_required_arguments_do_not_create_output(self):
        for arguments in ([], ["--name", "Only name"], ["--destination", str(self.target)]):
            with self.subTest(arguments=arguments):
                self.assertEqual(self.run_cli(*arguments).returncode, 2)
                self.assertFalse(self.target.exists())

    def test_unicode_names_spaced_paths_and_generated_document_links(self):
        self.assert_success(self.create("--stack", "python", name="Trợ lý dữ liệu 2026"))
        self.assertIn("Trợ lý dữ liệu 2026", (self.target / "README.md").read_text(encoding="utf-8"))
        self.assertIn("Hướng dẫn khi chọn Python", (self.target / "docs" / "stack-guide.md").read_text(encoding="utf-8"))
        for name in EXPECTED_DOCS:
            self.assertTrue((self.target / "docs" / name).is_file(), name)
        for name in GUIDES:
            self.assertTrue((self.target / "docs" / "guides" / name).is_file(), name)
        self.assertFalse((self.target / ".git").exists())
        self.assertFalse((self.target / "package.json").exists())
        self.assertFalse((self.target / "pyproject.toml").exists())
        self.assertNotIn("@RTK", (self.target / "AGENTS.md").read_text(encoding="utf-8"))
        self.assert_markdown_links_resolve(self.target)

    def test_all_stacks_only_change_instructions(self):
        for stack in ("python", "web", "undecided"):
            with self.subTest(stack=stack):
                target = self.base / ("stack " + stack)
                self.assert_success(self.create("--stack", stack, target=target))
                self.assertIn(f"`{stack}`", (target / "README.md").read_text(encoding="utf-8"))
                self.assertEqual(
                    (target / "docs" / "stack-guide.md").read_text(encoding="utf-8"),
                    (self.source / "templates" / "stacks" / f"{stack}.md").read_text(encoding="utf-8"),
                )

    def test_default_stack_is_undecided(self):
        self.assert_success(self.create())
        self.assertIn("`undecided`", (self.target / "README.md").read_text(encoding="utf-8"))

    def test_decomposed_unicode_name_is_normalized(self):
        self.assert_success(self.create(name=unicodedata.normalize("NFD", "  Trợ lý tiếng Việt  ")))
        self.assertTrue((self.target / "README.md").read_text(encoding="utf-8").startswith("# Trợ lý tiếng Việt\n"))

    def test_truly_empty_existing_directory_is_allowed(self):
        self.target.mkdir()
        self.assert_success(self.create())
        self.assertTrue((self.target / "README.md").is_file())

    def test_existing_contents_including_hidden_files_are_never_overwritten(self):
        for filename in ("README.md", ".gitkeep", ".DS_Store"):
            with self.subTest(filename=filename):
                target = self.base / ("occupied-" + filename.replace(".", "_"))
                target.mkdir()
                original = target / filename
                original.write_bytes(b"existing user data\x00\xff")
                before = original.read_bytes()
                result = self.create(target=target)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(original.read_bytes(), before)
                self.assertEqual(list(target.iterdir()), [original])

    def test_second_run_refuses_without_changing_first_run(self):
        self.assert_success(self.create())
        original = (self.target / "README.md").read_bytes()
        self.assertEqual(self.create(name="Different project").returncode, 2)
        self.assertEqual((self.target / "README.md").read_bytes(), original)

    def test_file_destination_is_preserved(self):
        self.target.write_text("user file", encoding="utf-8")
        self.assertEqual(self.create().returncode, 2)
        self.assertEqual(self.target.read_text(encoding="utf-8"), "user file")

    def test_project_name_cannot_escape_into_path_or_insert_control_characters(self):
        for name in ("../escape", "nested/name", r"nested\name", "..", ".", "   ", "name\nInjected", "name; command"):
            with self.subTest(name=name):
                self.assertEqual(self.create(name=name).returncode, 2)
                self.assertFalse(self.target.exists())

    def test_parent_relative_destination_is_normalized(self):
        self.assert_success(self.create(target="../sibling project", cwd=self.source))
        self.assertTrue((self.base / "sibling project" / "README.md").exists())

    def test_destination_inside_source_or_source_ancestor_is_refused(self):
        for target in (self.source, self.source / "new nested project", self.source / "tools" / "evals" / "copy", self.base):
            with self.subTest(target=target):
                self.assertEqual(self.create(target=target).returncode, 2)
        self.assertFalse((self.source / "new nested project").exists())
        self.assertFalse((self.source / "tools" / "evals" / "copy").exists())

    def test_symlink_destination_is_refused(self):
        outside = self.base / "real empty directory"
        outside.mkdir()
        try:
            self.target.symlink_to(outside, target_is_directory=True)
        except OSError as error:
            self.skipTest(f"Symlink privileges unavailable: {error}")
        self.assertEqual(self.create().returncode, 2)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(list(outside.iterdir()), [])

    def test_runtime_caches_evidence_and_secrets_are_not_copied(self):
        excluded = (
            "runs/old/results.json", "reports/old.html", "example-results/report.html",
            "old-results/data.json", "results/data.json", "artifacts/file.txt",
            "node_modules/module/index.js", ".venv/bin/python", ".venv-ragas/bin/python",
            ".playwright-browsers/browser/bin", "__pycache__/module.pyc", ".pytest_cache/state",
            ".ruff_cache/state", "._main.py", ".DS_Store", "framework.log", ".env", ".env.local",
        )
        for relative in excluded:
            self.write_source(relative, "sensitive old fixture artifact")
        self.assert_success(self.create())
        for relative in excluded:
            self.assertFalse((self.target / "tools" / "evals" / relative).exists(), relative)
        self.assertFalse((self.target / "tools" / "evals" / ".env.example").exists())
        self.assertFalse((self.target / ".env.example").exists())
        self.assertIn("EVAL_TARGET_API_KEY", (self.target / "docs" / "configuration.md").read_text(encoding="utf-8"))
        self.assert_markdown_links_resolve(self.target)

    def test_source_symlink_is_rejected_before_target_creation(self):
        outside = self.base / "external secret.txt"
        outside.write_text("must not copy", encoding="utf-8")
        try:
            (self.eval_source / "linked.txt").symlink_to(outside)
        except OSError as error:
            self.skipTest(f"Symlink privileges unavailable: {error}")
        self.assertEqual(self.create().returncode, 2)
        self.assertFalse(self.target.exists())

    def test_missing_source_input_does_not_touch_destination(self):
        (self.eval_source / "main.py").unlink()
        self.assertEqual(self.create().returncode, 2)
        self.assertFalse(self.target.exists())

    def test_generated_project_runs_after_move_and_source_removal(self):
        self.assert_success(self.create())
        moved = self.base / "moved independent project"
        self.target.rename(moved)
        shutil.rmtree(self.source)
        result = subprocess.run(
            [sys.executable, "-B", str(moved / "tools" / "evals" / "main.py"), "validate"],
            cwd=self.caller, capture_output=True, text=True, encoding="utf-8", timeout=30,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "fixture dataset resolved independently")
        self.assert_markdown_links_resolve(moved)

    def test_unicode_output_ignores_legacy_console_encoding(self):
        environment = dict(os.environ, PYTHONIOENCODING="cp1252")
        result = self.create(name="Dự án tiếng Việt", env=environment)
        self.assert_success(result)
        self.assertIn("Đã tạo bộ khởi đầu", result.stdout)
        self.assertTrue((self.target / "README.md").exists())
        error = self.create(env=environment)
        self.assertEqual(error.returncode, 2)
        self.assertIn("Không tạo được dự án", error.stderr)


if __name__ == "__main__":
    unittest.main()
