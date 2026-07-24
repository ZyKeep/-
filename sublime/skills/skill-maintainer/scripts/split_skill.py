#!/usr/bin/env python3
"""Dry-run or apply a simple level-two heading split for a large SKILL.md."""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.S)
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.M)


def slugify(title: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title.strip().lower()).strip("-")
    return slug or "section"


def make_filename(title: str, index: int, used: set[str]) -> str:
    base = slugify(title)
    if base == "section":
        base = f"section-{index:02d}"
    candidate = f"{base}.md"
    suffix = 2
    while candidate in used:
        candidate = f"{base}-{suffix}.md"
        suffix += 1
    used.add(candidate)
    return candidate


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


def split_sections(body: str) -> tuple[str, list[tuple[str, str]]]:
    matches = list(HEADING_RE.finditer(body))
    if not matches:
        return body, []
    intro = body[: matches[0].start()].rstrip() + "\n"
    sections: list[tuple[str, str]] = []
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(body)
        title = match.group(1).strip()
        content = body[match.start():end].strip() + "\n"
        sections.append((title, content))
    return intro, sections


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir")
    parser.add_argument("--apply", action="store_true", help="Write references and replace SKILL.md with a router.")
    parser.add_argument("--dry-run", action="store_true", help="Preview the split without writing files. This is the default.")
    parser.add_argument("--keep", type=int, default=3, help="Keep this many early sections in SKILL.md.")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir)
    skill_md = skill_dir / "SKILL.md"
    text = skill_md.read_text(encoding="utf-8-sig", errors="replace")
    front = FRONTMATTER_RE.match(text)
    if not front:
        raise SystemExit("SKILL.md has no YAML frontmatter")
    frontmatter = front.group(0)
    body = text[front.end():]
    intro, sections = split_sections(body)
    if not sections:
        raise SystemExit("No level-two sections found; manual split recommended")

    moved = sections[args.keep:]
    kept = sections[: args.keep]
    used_filenames: set[str] = set()
    moved_files = [
        (title, content, make_filename(title, index + 1, used_filenames))
        for index, (title, content) in enumerate(moved)
    ]
    print(f"Skill: {skill_dir.name}")
    print(f"Sections found: {len(sections)}")
    print(f"Kept in SKILL.md: {len(kept)}")
    print(f"Moved to references: {len(moved)}")
    for _, _, filename in moved_files:
        print(f"  references/{filename}")

    if not args.apply:
        print("Dry run only. Re-run with --apply after reviewing the plan.")
        return 0

    refs_dir = skill_dir / "references"
    refs_dir.mkdir(exist_ok=True)
    backup = unique_backup(skill_md)
    shutil.copy2(skill_md, backup)

    router_lines = [frontmatter.rstrip(), "", intro.rstrip(), ""]
    for title, content in kept:
        router_lines.extend([content.rstrip(), ""])
    router_lines.extend(["## Detailed References", ""])
    for title, content, filename in moved_files:
        (refs_dir / filename).write_text(content, encoding="utf-8")
        router_lines.append(f"- Read `references/{filename}` when the task needs {title} details.")
    skill_md.write_text("\n".join(router_lines).rstrip() + "\n", encoding="utf-8")
    print(f"Applied. Backup: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

