# Verification

- Scoped files: `qa-tools-storage/`, root README link, this plan directory.
- Shell syntax and Ruff passed.
- Disposable 512 MiB APFS sparsebundle lifecycle passed; image cleaned up.
- Portable doctor: 17/17 ready on the migrated runtime.
- Portable ZAP launcher: version 2.17.0.
- Real-volume identity check passed. No installed runtime or cache included in Git.
- Fresh full installation was not repeated; pins match previously verified installations.
- Existing report/PDF/template edits in the worktree are excluded from this commit.
