# Skill Layout Standard

Use this structure when creating or refactoring non-trivial skills:

```text
skill-name/
  SKILL.md
  docs/
  prompts/
  references/
  scripts/
```

## Folder Roles

- `SKILL.md`: Keep the trigger, the minimal workflow, and routing rules. It should tell Codex what to read or run next, not carry every detail.
- `docs/`: Put stage-specific operating rules here, such as prepare/run/validate flows, decision trees, and checklists.
- `prompts/`: Put reusable worker prompts and task templates here. Use them when a workflow delegates analysis, extraction, or validation.
- `references/`: Put optional libraries here, such as visual styles, API notes, historical bug cases, examples, schemas, and domain knowledge.
- `scripts/`: Put deterministic repeated actions here. Favor scripts for scanning, extracting, normalizing, generating reports, validating, transforming files, and batch operations.

## Script-First Rule

If an operation is repeated, mechanical, or easy to get subtly wrong, create or reuse a script before adding more prose to `SKILL.md`.

Good script candidates:

- environment checks
- dependency checks
- file inventory
- report skeleton generation
- fixed `rg` search bundles
- JSON/CSV/Excel/PDF extraction
- image preprocessing
- validation and lint wrappers
- batch copy, rename, or conversion

Keep judgment-heavy reasoning in docs or prompts. Keep deterministic work in scripts.

## Repository Packaging

For a public or shared repository:

- Put `README.md`, screenshots, install steps, and `CHANGELOG.md` at the repository root for humans.
- Put AI-facing instructions only inside the skill folder.
- Keep the skill folder portable so it can be copied into `C:\Users\ws\.codex\skills`.

## Refactor Target

Aim for:

- `SKILL.md` under 150 lines for normal skills.
- One-level links from `SKILL.md` to docs, prompts, references, and scripts.
- No duplicated content between `SKILL.md` and linked files.
- No process diary, broad README, or changelog inside the active skill folder.
