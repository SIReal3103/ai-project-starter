#!/usr/bin/env python3
"""Bundle selected guide sections with each standalone skill; --check never writes."""

import argparse
import hashlib
import json
from pathlib import Path
import re


def section_index(text: str) -> dict[str, tuple[int, int]]:
    """Index numbered and C1–I2 headings, ignoring headings inside code fences."""
    headings = []
    fence = None
    offset = 0
    for line in text.splitlines(keepends=True):
        match = re.match(r"^\s*(`{3,}|~{3,})(.*)$", line.rstrip())
        if match:
            marker, suffix = match.groups()
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1] and not suffix.strip():
                fence = None
        elif fence is None:
            match = re.match(r"^(#{2,6})\s+(\d+(?:\.\d+)*|[C-I][12])(?:\s|$)", line)
            if match:
                headings.append((match[2], len(match[1]), offset))
        offset += len(line)
    result = {}
    for i, (key, level, start) in enumerate(headings):
        if key in result:
            raise ValueError(f"Duplicate source section: {key}")
        end = next((pos for _, depth, pos in headings[i + 1:] if depth <= level), len(text))
        result[key] = (start, end)
    return result


def excerpt(text: str, sections: dict, keys: list[str]) -> str:
    missing = set(keys) - sections.keys()
    if missing:
        raise ValueError(f"Missing source sections: {', '.join(sorted(missing))}")
    ranges = sorted({sections[key] for key in keys}, key=lambda pair: (pair[0], -pair[1]))
    selected = []
    for start, end in ranges:
        if selected and start < selected[-1][1]:
            if end > selected[-1][1]:
                raise ValueError("Source sections overlap without containment")
            continue
        selected.append((start, end))
    return "\n\n".join(text[start:end].strip() for start, end in selected) + "\n"


def build_outputs(root: Path, only: str | None = None) -> dict[Path, bytes]:
    catalog = json.loads((root / "skills/catalog.json").read_text(encoding="utf-8"))
    source = root / catalog["source"]
    text = source.read_text(encoding="utf-8")
    sections = section_index(text)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    names = [entry["name"] for entry in catalog["skills"]]
    if len(set(names)) != len(names):
        raise ValueError("Duplicate skill names in catalog")
    if only and only not in names:
        raise ValueError(f"Unknown skill: {only}")
    outputs = {}
    for entry in catalog["skills"]:
        name = entry["name"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name) or len(name) > 64:
            raise ValueError(f"Invalid skill directory name: {name}")
        if only and name != only:
            continue
        # Resolve every requested section before writing any output.
        excerpt(text, sections, entry["primary_sections"])
        references = {
            "task-contract.md": [catalog["shared_contract_section"]],
            "techstack-guide.md": entry["source_sections"],
            "planning-handoff.md": catalog["planning_sections"],
        }
        for filename, keys in references.items():
            header = (
                f"<!-- Generated from {source.name}; sections {', '.join(keys)}; "
                f"sha256 {digest}. Edit the source and run scripts/sync-skills.py. -->\n\n"
                "Phần BTC chỉ áp dụng khi nhiệm vụ thuộc bối cảnh BTC; đường dẫn đội/vòng "
                "cần được xác nhận riêng. Model/API, budget và ngưỡng trong nguồn là snapshot "
                "hoặc đề xuất, không chứng minh quyền/capability/kết quả hiện tại.\n\n"
            )
            target = root / "skills" / name / "references" / filename
            outputs[target] = (header + excerpt(text, sections, keys)).encode("utf-8")
    return outputs


def synchronize(root: Path, check: bool = False, only: str | None = None) -> int:
    outputs = build_outputs(root, only)
    mismatches = []
    for path, expected in outputs.items():
        if path.is_file() and path.read_bytes() == expected:
            continue
        if check:
            mismatches.append(str(path.relative_to(root)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(expected)
    if mismatches:
        print("Missing or stale skill references:\n" + "\n".join(mismatches))
        return 1
    print(f"{'Checked' if check else 'Synchronized'} {len(outputs)} reference files.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify without writing")
    parser.add_argument("--skill", help="Only bundle this catalog skill")
    args = parser.parse_args()
    try:
        return synchronize(Path(__file__).resolve().parents[1], args.check, args.skill)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(2, f"Skill bundle error: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
