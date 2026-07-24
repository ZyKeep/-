#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from collections import defaultdict
from datetime import date
from pathlib import Path


SKILL_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a catalog and naming report for a Codex skills root."
    )
    parser.add_argument("root", help="Skills root, for example C:\\Users\\ws\\.codex\\skills")
    parser.add_argument("--out", help="Optional output markdown path")
    return parser.parse_args()


def bucket_for(name: str) -> str:
    if name.startswith("."):
        return "system"
    if "-" not in name:
        return "misc"
    return name.split("-", 1)[0]


def render(root: Path) -> str:
    dirs = sorted([p for p in root.iterdir() if p.is_dir()], key=lambda p: p.name.lower())
    files = sorted([p for p in root.iterdir() if p.is_file()], key=lambda p: p.name.lower())

    skill_dirs = [p for p in dirs if (p / "SKILL.md").exists()]
    support_dirs = [p for p in dirs if p not in skill_dirs]

    grouped: dict[str, list[str]] = defaultdict(list)
    for item in skill_dirs:
        grouped[bucket_for(item.name)].append(item.name)

    invalid_skill_names = [p.name for p in skill_dirs if not SKILL_NAME_RE.fullmatch(p.name)]
    root_instruction_files = [p.name for p in files if p.name.endswith(".instructions.md")]

    lines: list[str] = []
    lines.append("# Skills Index")
    lines.append("")
    lines.append(f"Generated on {date.today().isoformat()} from `{root}`.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Skill directories: {len(skill_dirs)}")
    lines.append(f"- Support directories: {len(support_dirs)}")
    lines.append(f"- Root files: {len(files)}")
    lines.append("")
    lines.append("## Skill Groups")
    lines.append("")

    for group in sorted(grouped):
        names = sorted(grouped[group])
        lines.append(f"### {group}")
        lines.append("")
        for name in names:
            lines.append(f"- `{name}`")
        lines.append("")

    lines.append("## Support Directories")
    lines.append("")
    if support_dirs:
        for item in support_dirs:
            lines.append(f"- `{item.name}`")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Root Files")
    lines.append("")
    if files:
        for item in files:
            lines.append(f"- `{item.name}`")
    else:
        lines.append("- None")
    lines.append("")

    lines.append("## Naming Notes")
    lines.append("")
    lines.append("- `SKILLS-CATALOG.md` is the official tier/domain routing view. This index remains a raw structural inventory grouped by name prefix.")
    if invalid_skill_names:
        lines.append("- Skill directories with non-standard names:")
        for name in invalid_skill_names:
            lines.append(f"  - `{name}`")
    else:
        lines.append("- All skill directories follow lowercase hyphen-case naming.")
    if root_instruction_files:
        lines.append(
            "- Root-level `*.instructions.md` files are global instruction files, not skill folders. "
            "Do not move them automatically."
        )
    if any(item.name == ".system" for item in support_dirs):
        lines.append("- `.system` is a reserved support directory and should stay in place.")
    if any(item.name == "my-instructions" for item in support_dirs):
        lines.append(
            "- `my-instructions` is acting as a support/archive folder. Keep it separate from skill folders."
        )
    lines.append("")

    lines.append("## Safe Reorganization Guidance")
    lines.append("")
    lines.append("- Add or update indexes and scripts freely.")
    lines.append("- Prefer refactoring inside existing skill folders over renaming active skill directories.")
    lines.append("- Rename a skill folder only when all references, triggers, and dependent instructions are verified.")
    lines.append(
        "- For heavy skills, keep `SKILL.md` short and move detailed rules into `docs/`, `references/`, or `scripts/`."
    )
    lines.append("")

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = Path(args.root)
    output = render(root)
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
    else:
        print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
