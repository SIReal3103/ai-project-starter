"""Verify the kit can run without the author’s runtime or working directory."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import main


class PortabilityTests(unittest.TestCase):
    def test_auto_discovery_ignores_home_and_unrelated_environments(self):
        with tempfile.TemporaryDirectory(prefix='eval discovery ') as folder:
            root = Path(folder)
            unrelated = root / 'unrelated environment'
            (unrelated / 'bin').mkdir(parents=True)
            (unrelated / 'bin/python').touch()
            env = {
                'HOME': str(root), 'VIRTUAL_ENV': str(unrelated),
                'EVAL_TOOL_ROOT': str(unrelated), 'PYTHONPATH': str(unrelated),
                'PATH': str(unrelated / 'bin'),
            }
            with patch.dict(os.environ, env, clear=True), patch.object(main, 'HERE', root):
                with patch.object(Path, 'home', side_effect=AssertionError('Home discovery is forbidden')):
                    self.assertIsNone(main.framework_python('ragas'))
                    self.assertIsNone(main.framework_python('deepeval'))

    def test_kit_local_environment_and_explicit_override(self):
        with tempfile.TemporaryDirectory(prefix='eval runtimes ') as folder:
            root = Path(folder)
            executable = Path('Scripts/python.exe') if os.name == 'nt' else Path('bin/python')
            local = root / '.venv-ragas' / executable
            local.parent.mkdir(parents=True)
            local.touch()
            # An invalid explicit choice must fail visibly instead of falling back.
            missing = root / 'explicit missing interpreter'
            with patch.dict(os.environ, {}, clear=True), patch.object(main, 'HERE', root):
                self.assertEqual(main.framework_python('ragas'), str(local))
                with patch.dict(os.environ, {'EVAL_RAGAS_PYTHON': str(missing)}):
                    self.assertEqual(main.framework_python('ragas'), str(missing))

    def test_child_environment_does_not_inherit_python_package_paths(self):
        with patch.dict(os.environ, {'PYTHONPATH': 'unrelated', 'PYTHONHOME': 'unrelated',
                                     'VIRTUAL_ENV': 'unrelated', 'CONDA_PREFIX': 'unrelated'}):
            env = main.clean_environment()
        for name in ('PYTHONPATH', 'PYTHONHOME', 'VIRTUAL_ENV', 'CONDA_PREFIX'):
            self.assertNotIn(name, env)
        self.assertEqual(env['PYTHONNOUSERSITE'], '1')

    def test_fresh_copy_demo_and_report_from_another_directory_with_spaces(self):
        with tempfile.TemporaryDirectory(prefix='eval portable ') as folder:
            root = Path(folder)
            kit = root / 'kit with spaces'
            shutil.copytree(ROOT, kit, ignore=shutil.ignore_patterns(
                '._*', '__pycache__', '.venv*', 'runs', 'node_modules', '*.log', '.playwright-browsers'))
            caller = root / 'caller with spaces'
            caller.mkdir()
            env = main.clean_environment()
            for name in ('EVAL_RAGAS_PYTHON', 'EVAL_DEEPEVAL_PYTHON'):
                env.pop(name, None)
            env['HOME'] = str(root / 'empty home')
            env['PYTHONTZPATH'] = ''
            commands = [
                [sys.executable, str(kit / 'main.py'), 'validate'],
                [sys.executable, str(kit / 'main.py'), 'demo', '--out', 'run with spaces'],
                [sys.executable, '-S', str(kit / 'report.py'), '--input', 'run with spaces/results.json',
                 '--output', 'report with spaces.html'],
            ]
            for command in commands:
                result = subprocess.run(command, cwd=caller, env=env, capture_output=True,
                                        text=True, encoding='utf-8', timeout=30)
                self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads((caller / 'run with spaces/results.json').read_text(encoding='utf-8'))
            self.assertEqual(report['summary']['passed'], 40)
            self.assertTrue(all(item['status'] == 'not_run' for item in report['frameworks']))
            self.assertTrue(all(item['detected'] for item in report['controls']))
            self.assertIn('chatbot-01', (caller / 'report with spaces.html').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
