# Local Repo Conventions

Use this reference when creating or updating a skill for `C:\Users\ws\.codex\skills`.

## Folder Standard

Minimum required files:

```text
skill-name/
  SKILL.md
  agents/
    openai.yaml
```

Optional folders, only when justified:

```text
docs/
prompts/
references/
scripts/
assets/
```

## Naming Rules

- Use lowercase hyphen-case.
- Keep names self-explanatory on first read.
- Prefer action or ownership in the name:
  - `codex-skill-author`
  - `qt-page-component-reuse`
  - `blueking-version-issue-query`
- Avoid generic names unless the repo already depends on them.

## Frontmatter Rules

Allowed keys:

- `name`
- `description`
- `license`
- `allowed-tools`
- `metadata`

Do not add:

- `version`
- `slug`
- `homepage`
- `changelog`

## Agents Metadata

Every local skill should include `agents/openai.yaml`.

Minimum interface fields:

- `display_name`
- `short_description`
- `default_prompt`

Keep these human readable and aligned with the frontmatter `description`.

## Release Tiers

- `promoted`: first-choice entrypoints
- `supported`: stable specialists
- `in-progress`: useful but still maturing
- `deprecated`: compatibility only

Default new skills to `in-progress` unless they already own a stable, repeatable workflow.

## Domain Buckets

Current catalog domains:

- `repo-operations`
- `qt-desktop`
- `mobiletrans`
- `blueking-ops`
- `spec-and-process`
- `artifact-generation`
- `analysis-and-guidance`
- `workspace-integration`

Choose the owning domain, not every possible domain.

## Resource Decision Rules

- Add `scripts/` when the same code would otherwise be re-written or when deterministic execution matters.
- Add `references/` when the detail is useful but should not always load into context.
- Add `docs/` when the workflow has phase-specific detail that should stay outside `SKILL.md`.
- Add `prompts/` only when reusable delegation or generation prompts exist.
- Add `assets/` only for output-side files such as templates, icons, or boilerplate payloads.

Do not create empty directories just because a template once used them.

## Post-Create Checklist

1. Validate the new skill with `.system/skill-creator/scripts/quick_validate.py`.
2. Refresh:
   - `SKILLS-CATALOG.md`
   - `SKILLS-INDEX.md`
   - `SKILLS-HYGIENE.md`
3. Confirm the new skill appears in `SKILLS-CATALOG.csv`.
4. If the skill replaced an existing broad workflow, update `codex-skills-router` references as needed.
