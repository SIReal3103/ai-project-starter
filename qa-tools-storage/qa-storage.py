#!/usr/bin/env python3
"""Manage a macOS APFS QA volume. Migration retains originals for verification."""

import argparse
import json
import os
import platform
import subprocess
import uuid
from pathlib import Path


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def save(path, data):
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n")
    temporary.replace(path)


def require_volume(storage, mount):
    config = json.loads((storage / "storage.json").read_text())
    if not mount.is_mount() or mount.is_symlink():
        raise RuntimeError("The QA volume must be mounted first.")
    if str(mount) != config["mount"]:
        raise RuntimeError("Mount does not match storage.json.")
    if (mount / ".qa-tools-volume-id").read_text().strip() != config["id"]:
        raise RuntimeError("The mounted volume belongs to another storage folder.")
    return config


def mount_volume(storage, mount):
    config = json.loads((storage / "storage.json").read_text())
    if str(mount) != config["mount"]:
        raise RuntimeError("Use the mount path recorded in storage.json.")
    if not mount.is_mount():
        if os.path.lexists(mount):
            raise RuntimeError("Mount path already exists; no data changed.")
        run(
            "hdiutil",
            "attach",
            "-nobrowse",
            "-mountpoint",
            str(mount),
            str(storage / "qa-runtime.sparsebundle"),
        )
    require_volume(storage, mount)
    print(f"Ready: {mount}")


def initialize(storage, mount, size):
    storage.mkdir(parents=True, exist_ok=True)
    image = storage / "qa-runtime.sparsebundle"
    if image.exists() or (storage / "storage.json").exists() or os.path.lexists(mount):
        raise RuntimeError("Storage/image/mount already exists. Use mount, not init.")
    run(
        "hdiutil",
        "create",
        "-size",
        size,
        "-type",
        "SPARSEBUNDLE",
        "-fs",
        "APFS",
        "-volname",
        mount.name,
        "-nospotlight",
        str(image),
    )
    run("hdiutil", "attach", "-nobrowse", "-mountpoint", str(mount), str(image))
    identifier = str(uuid.uuid4())
    (mount / ".qa-tools-volume-id").write_text(identifier + "\n")
    save(storage / "storage.json", {"id": identifier, "mount": str(mount)})
    for directory in ["runtime", "uv-tools", "caches"]:
        (mount / directory).mkdir()
    print(f"Created {image}; mounted at {mount}")


def migrate(storage, mount):
    require_volume(storage, mount)
    home = Path.home()
    pairs = [
        (home / ".local/share/ai-qa-tools", "runtime/ai-qa-tools"),
        (home / ".local/share/scope-data-bot-eval", "runtime/scope-data-bot-eval"),
        *[
            (home / ".local/share/uv/tools" / tool, "uv-tools/" + tool)
            for tool in ["semgrep", "bandit", "pip-audit"]
        ],
        (home / "Library/Caches/ms-playwright", "caches/ms-playwright"),
        (home / "Library/Caches/trivy", "caches/trivy"),
    ]
    log = storage / "migration.json"
    if log.exists():
        raise RuntimeError(
            "A migration manifest already exists; inspect it before retrying."
        )
    suffix = ".qa-move-backup-" + uuid.uuid4().hex[:12]
    entries = []
    for source, relative in pairs:
        if not os.path.lexists(source):
            continue
        destination = mount / relative
        backup = source.with_name(source.name + suffix)
        if source.is_symlink() or not source.is_dir():
            raise RuntimeError(f"Source is not a regular directory: {source}")
        if os.path.lexists(destination) or os.path.lexists(backup):
            raise RuntimeError(f"Destination or backup already exists: {destination}")
        entries.append(
            {
                "source": str(source),
                "destination": str(destination),
                "backup": str(backup),
                "checksum_verified": False,
                "switched": False,
                "backup_removed": False,
            }
        )
    if not entries:
        raise RuntimeError(
            "No existing QA runtime to move; follow the fresh-install guide."
        )
    manifest = {"mount": str(mount), "entries": entries}
    save(log, manifest)
    for entry in entries:
        source, destination = Path(entry["source"]), Path(entry["destination"])
        destination.parent.mkdir(parents=True, exist_ok=True)
        run("/usr/bin/ditto", str(source), str(destination))
        result = run(
            "/usr/bin/rsync",
            "-ainc",
            "--delete",
            str(source) + "/",
            str(destination) + "/",
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            raise RuntimeError(
                f"Checksum differences for {source}; originals retained."
            )
        entry["checksum_verified"] = True
        save(log, manifest)
    for entry in entries:
        source, backup = Path(entry["source"]), Path(entry["backup"])
        source.rename(backup)
        try:
            source.symlink_to(entry["destination"], target_is_directory=True)
        except BaseException:
            backup.rename(source)
            raise
        entry["switched"] = True
        save(log, manifest)
    print(
        "Copied, checksummed and linked. Internal backups retained; run QA checks next."
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=["init", "mount", "unmount", "migrate"])
    parser.add_argument("--storage-dir", required=True, type=Path)
    parser.add_argument("--mount", type=Path, default=Path("/Volumes/AI-QA-Tools"))
    parser.add_argument("--size", default="64g")
    args = parser.parse_args()
    if platform.system() != "Darwin":
        parser.error("APFS disk image management requires macOS.")
    storage = args.storage_dir.expanduser().resolve()
    mount = args.mount.expanduser().absolute()
    if not str(mount).startswith("/Volumes/") or mount.parent != Path("/Volumes"):
        parser.error("Mount must be a direct child of /Volumes.")
    if args.action == "init":
        initialize(storage, mount, args.size)
    elif args.action == "mount":
        mount_volume(storage, mount)
    elif args.action == "unmount":
        require_volume(storage, mount)
        run("hdiutil", "detach", str(mount))
    else:
        migrate(storage, mount)


if __name__ == "__main__":
    main()
