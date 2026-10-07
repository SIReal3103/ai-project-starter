# General AI story gameplay and reusable skill

Date: 2026-10-07
Status: Complete

Scope: Generic Vietnamese gameplay reference, reusable ai-story-gameplay skill, UI metadata and repository README discovery/installation. User requested GitHub publication. Existing unrelated uncommitted work remains outside this worktree and commit.

Decisions: Keep one canonical gameplay guide inside the portable skill. No fixed fictional world, model, contest, HP values or mandatory combat/voice across all projects. Preserve product-specific requirements when invoked. Design requests do not imply implementation permission.

Acceptance: Valid skill frontmatter/metadata, portable relative reference links, standalone guide, no machine paths or credentials, no unfinished scaffold. Manual scope checks: generic guide does not force one story; cozy request can omit combat; existing product requirements remain authoritative; design-only invocation does not build/deploy. No live inference or subagent evaluation performed.

Validation: Run skill-creator quick_validate, parse YAML and local Markdown links, git diff --check; review staged file list before commit. Publish only these task files and verify remote commit.
