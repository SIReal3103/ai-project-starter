# Publish external QA storage workflow

Status: Implementation and verification complete; ready to publish.

Verification: [report](reports/verification.md).

Scope: `qa-tools-storage/`, one root README link, this plan and its verification report. Preserve unrelated report changes in the working tree.

Acceptance: scripts choose paths at runtime; APFS image lifecycle verified on a disposable volume; migrated tools remain runnable; installer syntax and pinned package manifests checked; publish no runtime, cache, secrets or machine-specific home paths.

Rollback: revert the task commit; runtime migration on the user's SSD is unaffected by repository publication. See `qa-tools-storage/README.md` for runtime rollback.
