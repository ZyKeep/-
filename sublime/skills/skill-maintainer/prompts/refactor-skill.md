# Refactor Skill Prompt

Use this prompt when asking another worker to inspect one skill without loading unrelated local skills.

```text
Use the skill folder at {skill_dir}.

Goal: reduce token load while preserving behavior.

Rules:
- Read only this skill's SKILL.md and directly linked docs/prompts/references/scripts.
- Identify repeated mechanical work that should become scripts.
- Identify long sections that should move from SKILL.md into docs, prompts, or references.
- Do not delete content. Propose file moves and short router text.
- Return: current shape, proposed target layout, scripts to add, files to split, and validation command.
```
