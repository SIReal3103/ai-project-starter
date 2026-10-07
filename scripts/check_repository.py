#!/usr/bin/env python3
"""Validate portable paths, local Markdown links, and Python syntax."""

from __future__ import annotations

import argparse
import ast
import os
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {
    '.git', 'node_modules', '__pycache__', '.pytest_cache', '.hypothesis',
    '.ruff_cache', '.validation', '.playwright-browsers', 'runs', 'artifacts',
}
TEXT_SUFFIXES = {'.md', '.py', '.json', '.jsonl', '.toml', '.yml', '.yaml', '.sh', '.mjs', '.html', '.txt'}
MACHINE_PATH = re.compile(r'/(?:Users|Volumes|home|private/var/folders)/[^\s\)\]"<>]+|[A-Za-z]:\\(?:Users|Projects)\\')
LINK = re.compile(r'(?<!!)\[[^\]]*\]\((?:<([^>]+)>|([^\s\)]+))(?:\s+"[^"]*")?\)')


def ignored(name: str) -> bool:
    return name in IGNORED or name.startswith(('.venv', '._'))


def files(root: Path):
    for directory, subdirectories, filenames in os.walk(root, followlinks=False):
        subdirectories[:] = [name for name in subdirectories if not ignored(name)]
        for name in subdirectories[:]:
            child = Path(directory) / name
            if child.is_symlink():
                yield child
                subdirectories.remove(name)
        for name in filenames:
            if not ignored(name):
                yield Path(directory) / name


def check(root: Path = ROOT) -> int:
    root = root.resolve()
    if not root.is_dir():
        print('Repository directory does not exist.', file=sys.stderr)
        return 1
    errors = []
    count = 0
    for file in files(root):
        relative = file.relative_to(root)
        if file.is_symlink():
            if not file.resolve().is_relative_to(root) or not file.exists():
                errors.append(f'{relative}: symlink depends on an external or missing file')
            continue
        if file.suffix not in TEXT_SUFFIXES:
            continue
        try:
            content = file.read_text(encoding='utf-8')
        except UnicodeError:
            errors.append(f'{relative}: expected UTF-8')
            continue
        count += 1
        if MACHINE_PATH.search(content):
            errors.append(f'{relative}: hardcoded machine path')
        if file.suffix == '.py':
            try:
                ast.parse(content, filename=str(file))
            except SyntaxError as error:
                errors.append(f'{relative}:{error.lineno}: syntax {error.msg}')
        if file.suffix == '.md' and relative.parts[0] != 'templates':
            # Template links target generated files; generated-project tests check them.
            # Fenced examples describe future files without requiring them to exist.
            prose = re.sub(r'```.*?```', '', content, flags=re.S)
            for match in LINK.finditer(prose):
                target = unquote(match.group(1) or match.group(2))
                parsed = urlsplit(target)
                if parsed.scheme or parsed.netloc or target.startswith('#'):
                    continue
                destination = (file.parent / parsed.path).resolve()
                if not destination.is_relative_to(root):
                    errors.append(f'{relative}: link escapes repo: {target}')
                elif not destination.exists():
                    errors.append(f'{relative}: missing link: {target}')
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'Checked {count} text files: local links, machine-path portability and Python syntax pass.')
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT, help='Also accepts a generated project directory')
    raise SystemExit(check(parser.parse_args().root))
