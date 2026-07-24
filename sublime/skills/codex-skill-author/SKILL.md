---
name: codex-skill-author
description: >
  Use when creating or updating a local Codex skill in `C:\Users\ws\.codex\skills`,
  especially when the repo needs a repo-compliant scaffold, `agents/openai.yaml`,
  release tier/domain registration, or a refactor that turns repeated know-how into a
  reusable local skill.
---

# Codex Skill Author

Use this skill to author local skills that match this repository's conventions. This is the repo-specific companion to the system `skill-creator`: it specializes for this local skills root, local catalog buckets, and local maintenance workflow.

## Trigger

- The user asks to create a new local skill, turn a repeated workflow into a skill, or refactor a draft skill into this repo.
- A new skill needs local repo metadata such as `agents/openai.yaml`, a catalog tier/domain entry, or generated repo indexes.
- An existing local skill should be reorganized to use scripts, references, prompts, or docs more effectively.

## Workflow

1. Collect the smallest set of inputs needed to scaffold the skill:
   - skill name
   - trigger description
   - domain bucket
   - release tier
   - whether the skill should be an entrypoint
   - which resource folders are actually needed
2. Read `references/local-repo-conventions.md` before creating or reshaping the skill.
3. If the skill is analysis, reporting, metrics, dashboard, or decision oriented, also read `references/decision-ready-analysis-patterns.md`.
4. Run `scripts/init_local_skill.py` to create the local skill folder, `SKILL.md`, `agents/openai.yaml`, optional resource folders, and a `SKILLS-CATALOG.csv` row.
5. Replace scaffold TODOs with the real workflow. Keep `SKILL.md` short; move detail into `docs/`, `references/`, `prompts/`, or `scripts/`.
6. Refresh the repo views:
   - `skill-maintainer/scripts/render_skill_catalog.py`
   - `skill-maintainer/scripts/render_skills_index.py`
   - `skill-maintainer/scripts/audit_skill_hygiene.py`
7. Validate the resulting skill with `.system/skill-creator/scripts/quick_validate.py`.

## Hard Rules

- Do not create empty helper directories by default. Only create `docs/`, `prompts/`, `references/`, or `scripts/` when the skill actually needs them.
- Do not add marketplace-style frontmatter such as `version`, `slug`, `homepage`, or `changelog`; this repo's validator rejects them.
- Do not introduce `.skill` packaging steps for local repo work; this repo uses live folders under `C:\Users\ws\.codex\skills`.
- Default new skills to `in-progress` unless there is a clear reason they should start as `supported` or `promoted`.
- Prefer scripts for repeated deterministic work; prefer references for detailed, selective context; prefer prompts only when delegation templates are genuinely reusable.
