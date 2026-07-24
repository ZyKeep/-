#!/usr/bin/env python3
"""Move a large SKILL.md body into docs and leave a small routing entrypoint."""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.S)
DETAILED_REFS = "## Detailed References"


def unique_backup(path: Path) -> Path:
    candidate = path.with_suffix(path.suffix + ".bak")
    if not candidate.exists():
        return candidate
    index = 2
    while True:
        candidate = path.with_suffix(path.suffix + f".bak{index}")
        if not candidate.exists():
            return candidate
        index += 1


def compact(skill_dir: Path, doc_name: str, apply: bool) -> int:
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8-sig", errors="replace")
    front = FRONTMATTER_RE.match(text)
    if not front:
        raise SystemExit("SKILL.md has no YAML frontmatter")

    frontmatter = front.group(0).rstrip()
    body = text[front.end():].strip()
    title_match = re.search(r"^#\s+(.+?)\s*$", body, re.M)
    title = title_match.group(0) if title_match else f"# {skill_dir.name}"

    refs_index = body.find(DETAILED_REFS)
    if refs_index >= 0:
        core_body = body[:refs_index].strip()
        detailed_refs = body[refs_index:].strip()
    else:
        core_body = body.strip()
        detailed_refs = ""

    if not core_body:
        raise SystemExit("No body content found to compact")

    doc_rel = f"docs/{doc_name}"
    print(f"Skill: {skill_dir.name}")
    print(f"Move core body to: {doc_rel}")
    print(f"Keep detailed references section: {'yes' if detailed_refs else 'no'}")
    if not apply:
        print("Dry run only. Re-run with --apply after reviewing the plan.")
        return 0

    docs_dir = skill_dir / "docs"
    docs_dir.mkdir(exist_ok=True)
    doc_path = docs_dir / doc_name
    if doc_path.exists():
        raise SystemExit(f"Refusing to overwrite existing {doc_path}")

    backup = unique_backup(skill_md)
    shutil.copy2(skill_md, backup)
    doc_path.write_text(core_body.rstrip() + "\n", encoding="utf-8")

    router_lines = [
        frontmatter,
        "",
        title,
        "",
        "Use this file as the lightweight entrypoint. Load detailed context only when the task needs it.",
        "",
        "## Workflow",
        "",
        f"1. Read `{doc_rel}` for the core workflow before doing substantive work with this skill.",
        "2. Read only the specific linked reference files needed for the current task.",
        "3. Prefer scripts or structured artifacts for repeated extraction, reporting, or validation work.",
        "4. Keep long evidence, templates, historical notes, and examples out of `SKILL.md`.",
        "",
        "## Resource Guide",
        "",
        f"- `docs/{doc_name}`: core workflow and stage rules moved from the original `SKILL.md`.",
    ]
    if detailed_refs:
        router_lines.extend(["", detailed_refs])
    skill_md.write_text("\n".join(router_lines).rstrip() + "\n", encoding="utf-8")
    print(f"Applied. Backup: {backup}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir")
    parser.add_argument("--doc-name", default="core-workflow.md")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--dry-run", action="store_true", help="Preview only. This is the default.")
    args = parser.parse_args()
    return compact(Path(args.skill_dir), args.doc_name, args.apply)


if __name__ == "__main__":
    raise SystemExit(main())
