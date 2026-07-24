---
name: skill-maintainer
description: "Use to audit and slim local Codex skills: find token-heavy SKILL.md or descriptions, split long guidance into docs/references/prompts, add scripts, scaffold layout, and validate skills."
---

# Skill Maintainer

Keep skill maintenance cheap: inspect first with scripts, then read only the target skill files that need manual judgment. Prefer executable scripts and split context over long prose.

## Preferred Layout

Use this layout for new or refactored skills when the skill is more than a tiny one-file rule:

```text
skill-name/
  SKILL.md      # workflow skeleton and routing only
  docs/         # phase-specific detailed rules, loaded on demand
  prompts/      # worker/task prompt templates
  references/   # optional domain, visual, API, or style libraries
  scripts/      # deterministic repeated actions
```

For repository-packaged skills, keep `README.md` and `CHANGELOG.md` at the repository root for humans. Keep AI-facing material inside the skill folder.

## Workflow

1. Run `scripts/audit_skills.py <skills-root> --out <report.md>` to inventory all local skills by `SKILL.md` size, line count, resource folders, and refactor priority.
   For repo-compliant new skill creation, prefer `codex-skill-author` first; use this skill after the scaffold exists or when reorganizing an existing skill.
2. For large pure-text skills, use the report to choose one or more actions:
   - Move phase-specific operating rules into `docs/`.
   - Move task delegation templates into `prompts/`.
   - Move detailed domain notes, examples, visual styles, API tables, and history into `references/`.
   - Add deterministic helper scripts under `scripts/` for repeated search, extraction, reporting, conversion, validation, or file generation.
   - Keep `SKILL.md` as a short router that says when to read each reference or run each script.
3. For a new skill layout, run `scripts/scaffold_layout.py <skill-dir>` to create `docs/`, `prompts/`, `references/`, and `scripts/` with minimal placeholders.
4. For a candidate split, run `scripts/split_skill.py <skill-dir> --dry-run` first. Only use `--apply` after reviewing the generated plan.
5. If the remaining `SKILL.md` is still too large, run `scripts/compact_skill_router.py <skill-dir> --dry-run` to move the core body into `docs/core-workflow.md`.
6. Maintain `SKILLS-CATALOG.csv` as the source of truth for release tiers and business-domain buckets when the repo taxonomy changes.
7. Run `scripts/render_skill_catalog.py <skills-root> --catalog <skills-root>\SKILLS-CATALOG.csv --out <skills-root>\SKILLS-CATALOG.md` after adding skills or changing buckets.
8. Validate changed skills with `skill-creator/scripts/quick_validate.py <skill-dir>`.

## Resource Guide

- Read `docs/layout-standard.md` before creating or reorganizing a skill folder.
- Prefer `codex-skill-author` when the task is to create a new local skill with `agents/openai.yaml` and catalog registration.
- Read `references/refactor-patterns.md` before doing manual edits to an existing skill.
- Prefer `audit_skills.py` for broad inventory instead of reading every `SKILL.md`.
- Prefer `render_skill_catalog.py` when the task is to refresh the official promoted/supported/in-progress/deprecated view.
- Prefer `split_skill.py --dry-run` when a single `SKILL.md` has many level-two sections and no `references/` folder.
- Prefer `compact_skill_router.py --dry-run` when a previously split skill still keeps a long core workflow in `SKILL.md`.

## Defaults

- Target root: `C:\Users\ws\.codex\skills`.
- Treat `SKILL.md` over 10 KB with no references/scripts as high priority.
- Keep active `SKILL.md` files under roughly 150 lines when possible.
- When a process repeats twice, consider turning it into a script before adding more prose.
- Do not delete original content during an automated split; keep a `.bak` file when applying.

