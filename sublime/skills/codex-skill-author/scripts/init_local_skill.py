#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from pathlib import Path
from textwrap import dedent

import yaml


TIER_CHOICES = ("promoted", "supported", "in-progress", "deprecated")
DOMAIN_CHOICES = (
    "repo-operations",
    "qt-desktop",
    "mobiletrans",
    "blueking-ops",
    "spec-and-process",
    "artifact-generation",
    "analysis-and-guidance",
    "workspace-integration",
)
RESOURCE_CHOICES = ("docs", "prompts", "references", "scripts", "assets")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a repo-compliant local Codex skill scaffold and register it in SKILLS-CATALOG.csv."
    )
    parser.add_argument("skill_name", help="Hyphen-case skill name")
    parser.add_argument("--description", required=True, help="Frontmatter description used for triggering")
    parser.add_argument("--domain", choices=DOMAIN_CHOICES, required=True, help="Catalog domain bucket")
    parser.add_argument("--tier", choices=TIER_CHOICES, default="in-progress", help="Catalog release tier")
    parser.add_argument("--path", type=Path, default=None, help="Skills root; defaults to the local Codex skills root")
    parser.add_argument("--entrypoint", action="store_true", help="Register the skill as a default entrypoint")
    parser.add_argument(
        "--resources",
        default="",
        help="Comma-separated optional folders to create: docs,prompts,references,scripts,assets",
    )
    parser.add_argument("--examples", action="store_true", help="Create lightweight placeholder files in optional folders")
    parser.add_argument("--display-name", default=None, help="Override agents/openai.yaml display name")
    parser.add_argument("--short-description", default=None, help="Override agents/openai.yaml short description")
    parser.add_argument("--default-prompt", default=None, help="Override agents/openai.yaml default prompt")
    parser.add_argument("--skip-catalog", action="store_true", help="Create files but do not edit SKILLS-CATALOG.csv")
    return parser.parse_args()


def title_case(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("-"))


def parse_resources(raw: str) -> list[str]:
    if not raw.strip():
        return []
    items = []
    for part in raw.split(","):
        value = part.strip()
        if not value:
            continue
        if value not in RESOURCE_CHOICES:
            raise ValueError(f"Unsupported resource folder: {value}")
        if value not in items:
            items.append(value)
    return items


def build_skill_body(skill_name: str, display_name: str, resources: list[str]) -> str:
    resource_guidance = []
    if "docs" in resources:
        resource_guidance.append("- Move long phase-specific detail into `docs/`.")
    if "references" in resources:
        resource_guidance.append("- Load `references/` files only when the task needs them.")
    if "prompts" in resources:
        resource_guidance.append("- Keep reusable delegation or generation prompts under `prompts/`.")
    if "scripts" in resources:
        resource_guidance.append("- Put repeated deterministic work under `scripts/` and call it directly.")
    if "assets" in resources:
        resource_guidance.append("- Keep output-side templates or payloads under `assets/`.")
    if not resource_guidance:
        resource_guidance.append("- Add `docs/`, `references/`, `prompts/`, `scripts/`, or `assets/` only when the skill proves it needs them.")

    lines = [
        f"# {display_name}",
        "",
        f"Use this skill when the user needs the workflow owned by `{skill_name}`.",
        "",
        "## Trigger",
        "",
        "- TODO: Replace with the concrete user requests, files, or conditions that should trigger this skill.",
        "- TODO: Name the narrow owning scope so the router can choose this skill confidently.",
        "",
        "## Workflow",
        "",
        "1. Confirm the exact user outcome, the affected files or artifacts, and the smallest safe scope.",
        "2. Inspect the real project or artifact before making claims or edits.",
        "3. Load only the smallest relevant bundled resources for this task.",
    ]
    step_index = 4
    for item in resource_guidance:
        lines.append(f"{step_index}. {item[2:] if item.startswith('- ') else item}")
        step_index += 1
    lines.extend(
        [
            f"{step_index}. Produce the requested result and verify it with the smallest relevant validation path.",
            f"{step_index + 1}. Replace or remove scaffold TODOs before relying on this skill in real work.",
            "",
            "## Hard Rules",
            "",
            "- Keep `SKILL.md` short and move detail outward instead of growing a monolith.",
            "- Do not add non-repo frontmatter such as `version`, `slug`, `homepage`, or `changelog`.",
            "- Prefer scripts for repeated deterministic work and references for detailed selective context.",
        ]
    )
    return "\n".join(lines) + "\n"


def create_openai_yaml(args: argparse.Namespace, skill_name: str, display_name: str) -> dict:
    short_description = args.short_description or args.description.split(".")[0].strip()
    if not short_description:
        short_description = f"Use the {display_name} workflow"
    default_prompt = args.default_prompt or (
        f"Use ${skill_name} to handle this task with the repo's dedicated workflow and resources."
    )
    return {
        "interface": {
            "display_name": args.display_name or display_name,
            "short_description": short_description,
            "default_prompt": default_prompt,
        }
    }


def write_yaml(path: Path, data: dict) -> None:
    path.write_text(
        yaml.safe_dump(data, allow_unicode=True, sort_keys=False).rstrip() + "\n",
        encoding="utf-8",
    )


def write_skill_md(path: Path, skill_name: str, description: str, body: str) -> None:
    frontmatter = yaml.safe_dump(
        {"name": skill_name, "description": description},
        allow_unicode=True,
        sort_keys=False,
    ).rstrip()
    path.write_text(f"---\n{frontmatter}\n---\n\n{body}", encoding="utf-8")


def create_placeholder(path: Path, content: str) -> None:
    path.write_text(dedent(content).lstrip(), encoding="utf-8")


def update_catalog(catalog_path: Path, skill_name: str, tier: str, domain: str, entrypoint: bool) -> None:
    with catalog_path.open("r", encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))

    if any(row["name"] == skill_name for row in rows):
        raise ValueError(f"Skill already exists in catalog: {skill_name}")

    rows.append(
        {
            "name": skill_name,
            "tier": tier,
            "domain": domain,
            "entrypoint": "true" if entrypoint else "false",
        }
    )
    rows.sort(key=lambda row: row["name"])

    with catalog_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "tier", "domain", "entrypoint"])
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    args = parse_args()
    resources = parse_resources(args.resources)
    skills_root = (args.path or Path(__file__).resolve().parents[2]).resolve()
    skill_dir = skills_root / args.skill_name
    catalog_path = skills_root / "SKILLS-CATALOG.csv"

    if skill_dir.exists():
        raise SystemExit(f"Refusing to overwrite existing skill directory: {skill_dir}")
    if not catalog_path.exists() and not args.skip_catalog:
        raise SystemExit(f"Catalog not found: {catalog_path}")

    display_name = args.display_name or title_case(args.skill_name)

    skill_dir.mkdir(parents=True, exist_ok=False)
    (skill_dir / "agents").mkdir()
    for folder in resources:
        (skill_dir / folder).mkdir()

    write_skill_md(
        skill_dir / "SKILL.md",
        args.skill_name,
        args.description,
        build_skill_body(args.skill_name, display_name, resources),
    )
    write_yaml(skill_dir / "agents" / "openai.yaml", create_openai_yaml(args, args.skill_name, display_name))

    if args.examples:
        if "docs" in resources:
            create_placeholder(
                skill_dir / "docs" / "core-workflow.md",
                """
                # Core Workflow

                Replace this file with the phase-specific rules that are too detailed for `SKILL.md`.
                """,
            )
        if "references" in resources:
            create_placeholder(
                skill_dir / "references" / "domain-notes.md",
                """
                # Domain Notes

                Replace this file with detailed domain rules, schemas, examples, or edge cases.
                """,
            )
        if "prompts" in resources:
            create_placeholder(
                skill_dir / "prompts" / "task-template.md",
                """
                You are helping with `TODO`.
                Replace this with a real reusable prompt only if the pattern actually repeats.
                """,
            )
        if "scripts" in resources:
            create_placeholder(
                skill_dir / "scripts" / "example.py",
                """
                #!/usr/bin/env python3
                from __future__ import annotations

                def main() -> None:
                    print("Replace this placeholder with a real deterministic helper.")

                if __name__ == "__main__":
                    main()
                """,
            )
        if "assets" in resources:
            create_placeholder(
                skill_dir / "assets" / "placeholder.txt",
                """
                Replace this placeholder with a real template, icon, boilerplate payload, or other output-side asset.
                """,
            )

    if not args.skip_catalog:
        update_catalog(catalog_path, args.skill_name, args.tier, args.domain, args.entrypoint)

    print(f"Created skill scaffold: {skill_dir}")
    print(f"Resources: {', '.join(resources) if resources else 'none'}")
    if not args.skip_catalog:
        print(f"Registered in catalog: {catalog_path}")
    print("Next steps:")
    print("1. Replace scaffold TODOs in SKILL.md")
    print("2. Refresh SKILLS-CATALOG.md, SKILLS-INDEX.md, and SKILLS-HYGIENE.md")
    print("3. Validate with .system/skill-creator/scripts/quick_validate.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
