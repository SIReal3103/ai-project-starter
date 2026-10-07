#!/usr/bin/env python3
"""Create an independent planning and eval starter without overwriting files."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import sys
import tempfile
import unicodedata


ROOT = Path(__file__).resolve().parents[1]
STACKS = ("python", "web", "undecided")
EXCLUDED_DIRS = {
    ".git", "node_modules", "runs", "reports", "example-results", "old-results",
    "results", "artifacts", "__pycache__", ".pytest_cache", ".mypy_cache",
    ".ruff_cache", ".cache", ".tox", ".nox", "venv", "env", "coverage",
    "htmlcov", "dist", "build", ".playwright-browsers",
}
REQUIRED_EVAL_FILES = (
    "README.md", "main.py", "scoring.py", "report.py", "agent-guide.md",
    "adapters/demo.py", "datasets/demo-cases.jsonl", "templates/report-template.html",
)


class ScaffoldError(Exception):
    """A precondition or copy failure that should be reported without a traceback."""


def validate_name(name: str) -> str:
    name = unicodedata.normalize("NFC", name.strip())
    if not name or len(name) > 100 or name in (".", ".."):
        raise ScaffoldError("Tên dự án phải có 1–100 ký tự và không phải . hoặc ..")
    if not any(char.isalnum() for char in name):
        raise ScaffoldError("Tên dự án cần có ít nhất một chữ hoặc số.")
    if any(not (char.isalnum() or char in " ._-") for char in name):
        raise ScaffoldError("Tên chỉ nhận chữ, số, khoảng trắng, dấu chấm, gạch dưới và gạch nối; không nhận đường dẫn.")
    return name


def destination_path(raw_path: str) -> Path:
    if not raw_path.strip():
        raise ScaffoldError("Cần đường dẫn đích không rỗng.")
    candidate = Path(raw_path).expanduser()
    if candidate.is_symlink():
        raise ScaffoldError("Không tạo dự án qua symlink ở thư mục đích.")
    candidate = candidate.resolve()
    if candidate == ROOT or ROOT in candidate.parents or candidate in ROOT.parents:
        raise ScaffoldError("Đích không được chồng lên repo starter nguồn hoặc nằm bên trong nó.")
    if candidate.exists():
        if not candidate.is_dir() or any(candidate.iterdir()):
            raise ScaffoldError("Đích phải chưa tồn tại hoặc là thư mục thật sự rỗng, kể cả tệp ẩn.")
    return candidate


def excluded(path: Path) -> bool:
    name = path.name
    if name.startswith("._") or name == ".DS_Store" or name.startswith(".venv"):
        return True
    if name in EXCLUDED_DIRS:
        return True
    if name in (".env", ".coverage") or name.startswith(".coverage."):
        return True
    if name.startswith(".env."):
        return True
    return path.suffix in (".pyc", ".pyo", ".log")


def copy_eval_tree(source: Path, destination: Path) -> None:
    """Copy only source inputs, without following links into another checkout."""
    if source.is_symlink():
        raise ScaffoldError("Bộ eval nguồn không được là symlink.")
    destination.mkdir()
    for entry in sorted(source.iterdir()):
        if excluded(entry):
            continue
        target = destination / entry.name
        if entry.is_symlink():
            raise ScaffoldError(f"Bộ eval có symlink không thể mang sang dự án độc lập: {entry.name}")
        if entry.is_dir():
            copy_eval_tree(entry, target)
        elif entry.is_file():
            shutil.copyfile(entry, target)
            target.chmod(entry.stat().st_mode & 0o777)
        else:
            raise ScaffoldError(f"Bộ eval có loại tệp không hỗ trợ: {entry.name}")


def prepare_staging(stage: Path, name: str, stack: str) -> None:
    project_templates = ROOT / "templates" / "project"
    stack_template = ROOT / "templates" / "stacks" / f"{stack}.md"
    eval_readme_template = ROOT / "templates" / "eval-kit-readme.md"
    eval_source = ROOT / "tools" / "evals"
    guides_source = ROOT / "docs" / "guides"
    if not project_templates.is_dir() or not stack_template.is_file() or not eval_readme_template.is_file():
        raise ScaffoldError("Thiếu templates trong starter; cần clone/copy đầy đủ repo.")
    if project_templates.is_symlink() or eval_readme_template.is_symlink():
        raise ScaffoldError("Template không được là symlink.")
    if not guides_source.is_dir() or not (guides_source / "architecture-and-use-cases.md").is_file():
        raise ScaffoldError("Thiếu bộ hướng dẫn trong docs/guides; cần clone/copy đầy đủ repo.")
    if eval_source.is_symlink():
        raise ScaffoldError("Bộ eval nguồn không được là symlink.")
    missing = [name for name in REQUIRED_EVAL_FILES if not (eval_source / name).is_file()]
    if missing:
        raise ScaffoldError("Thiếu mã nguồn eval bắt buộc: " + ", ".join(missing))
    for source in sorted(project_templates.rglob("*")):
        if source.is_symlink():
            raise ScaffoldError("Template không được chứa symlink.")
        relative = source.relative_to(project_templates)
        target = stage / relative
        if source.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            content = source.read_text(encoding="utf-8")
            content = content.replace("{{PROJECT_NAME}}", name).replace("{{STACK}}", stack)
            target.write_text(content, encoding="utf-8")
    if stack_template.is_symlink():
        raise ScaffoldError("Hướng dẫn stack không được là symlink.")
    (stage / "docs" / "stack-guide.md").write_text(stack_template.read_text(encoding="utf-8"), encoding="utf-8")
    (stage / "tools").mkdir(exist_ok=True)
    copy_eval_tree(eval_source, stage / "tools" / "evals")
    # The copied kit omits example snapshots; its README links only to source docs.
    (stage / "tools" / "evals" / "README.md").write_text(eval_readme_template.read_text(encoding="utf-8"), encoding="utf-8")
    copy_eval_tree(guides_source, stage / "docs" / "guides")


def publish_staging(stage: Path, destination: Path) -> None:
    """Use exclusive creation for every file; preserve any concurrent user writes."""
    try:
        destination.mkdir()
    except FileExistsError:
        if destination.is_symlink() or not destination.is_dir() or any(destination.iterdir()):
            raise ScaffoldError("Đích đã có dữ liệu hoặc đổi loại trong khi chuẩn bị; không ghi đè.") from None
    lock = destination / ".starter-creation-lock"
    try:
        with lock.open("x", encoding="utf-8") as handle:
            handle.write("Project starter creation in progress.\n")
    except FileExistsError:
        raise ScaffoldError("Có lượt tạo dự án khác đang dùng đích này; không ghi đè.") from None
    try:
        if any(path != lock for path in destination.iterdir()):
            raise ScaffoldError("Đích xuất hiện dữ liệu mới; không ghi đè.")
        for source in sorted(stage.rglob("*")):
            target = destination / source.relative_to(stage)
            if source.is_dir():
                target.mkdir()
            else:
                with source.open("rb") as reader, target.open("xb") as writer:
                    shutil.copyfileobj(reader, writer)
                target.chmod(source.stat().st_mode & 0o777)
    finally:
        lock.unlink(missing_ok=True)


def create_project(name: str, destination: str, stack: str) -> Path:
    name = validate_name(name)
    if stack not in STACKS:
        raise ScaffoldError("Stack không được hỗ trợ.")
    target = destination_path(destination)
    # Build before touching the destination, so missing templates leave it intact.
    with tempfile.TemporaryDirectory(prefix="ai-project-starter-") as temporary:
        stage = Path(temporary)
        prepare_staging(stage, name, stack)
        target.parent.mkdir(parents=True, exist_ok=True)
        publish_staging(stage, target)
    return target


def main() -> int:
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="backslashreplace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--name", required=True, help="Tên hiển thị; không dùng như đường dẫn")
    parser.add_argument("--destination", required=True, help="Thư mục đích mới hoặc thật sự rỗng")
    parser.add_argument("--stack", choices=STACKS, default="undecided", help="Chọn hướng dẫn, không sinh app hay cài dependency")
    args = parser.parse_args()
    try:
        target = create_project(args.name, args.destination, args.stack)
    except (ScaffoldError, OSError, UnicodeError) as error:
        print(f"Không tạo được dự án: {error}", file=sys.stderr)
        return 2
    print(f"Đã tạo bộ khởi đầu tại: {target}")
    print("Đọc README.md và docs/project-brief.md. Sản phẩm chưa được triển khai.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
