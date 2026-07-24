#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from collections import defaultdict
from pathlib import Path


BACKUP_SUFFIXES = (".bak", ".bak2", ".descbak", ".fmbak", ".orig", ".original")
SECTION_RE = re.compile(r"^section-\d+\.md$")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit skill hygiene gaps such as missing agents and section-style filenames.")
    parser.add_argument("root", help="Skills root")
    parser.add_argument("--out", help="Optional markdown report path")
    return parser.parse_args()


def render_report(root: Path) -> str:
    skills = sorted([p for p in root.iterdir() if p.is_dir() and (p / "SKILL.md").exists()], key=lambda p: p.name)
    missing_agents: list[str] = []
    missing_scripts: list[str] = []
    standalone_names: list[str] = []
    section_files: list[str] = []
    backup_files: list[str] = []

    for skill in skills:
        if not (skill / "agents" / "openai.yaml").exists():
            missing_agents.append(skill.name)
        if not (skill / "scripts").exists():
            missing_scripts.append(skill.name)
        if "-" not in skill.name:
            standalone_names.append(skill.name)
        for file in skill.rglob("*"):
            if file.is_file():
                if SECTION_RE.fullmatch(file.name):
                    section_files.append(str(file.relative_to(root)))
                if any(file.name.endswith(suffix) for suffix in BACKUP_SUFFIXES):
                    backup_files.append(str(file.relative_to(root)))

    lines: list[str] = []
    lines.append("# Skills Hygiene Report")
    lines.append("")
    lines.append(f"- Skills scanned: {len(skills)}")
    lines.append(f"- Missing `agents/openai.yaml`: {len(missing_agents)}")
    lines.append(f"- Missing `scripts/`: {len(missing_scripts)}")
    lines.append(f"- Standalone-name candidates: {len(standalone_names)}")
    lines.append(f"- `section-XX.md` files: {len(section_files)}")
    lines.append(f"- Backup-like files inside skills: {len(backup_files)}")
    lines.append("")

    sections: dict[str, list[str]] = defaultdict(list)
    sections["Missing agents/openai.yaml"] = missing_agents
    sections["Missing scripts directory"] = missing_scripts
    sections["Standalone-name candidates"] = standalone_names
    sections["Author-centric section filenames"] = section_files
    sections["Backup-like files"] = backup_files

    for title, items in sections.items():
        lines.append(f"## {title}")
        lines.append("")
        if items:
            for item in items:
                lines.append(f"- `{item}`")
        else:
            lines.append("- None")
        lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append("- A standalone name is not automatically wrong, but it is worth checking for discoverability.")
    lines.append("- Missing `scripts/` is only a candidate hygiene gap. Add scripts when deterministic repeated work exists.")
    lines.append("- `section-XX.md` filenames are valid but usually weaker than descriptive names for long-term maintenance.")
    lines.append("- Backup-like files should usually move out of active skill folders once the refactor is stable.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    report = render_report(Path(args.root))
    if args.out:
        Path(args.out).write_text(report, encoding="utf-8")
    else:
        print(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
