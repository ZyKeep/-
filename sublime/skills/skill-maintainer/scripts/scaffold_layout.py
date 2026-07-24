#!/usr/bin/env python3
"""Create the preferred docs/prompts/references/scripts layout for a skill."""
from __future__ import annotations

import argparse
from pathlib import Path

PLACEHOLDERS = {
    "docs": "# Docs\n\nPut phase-specific detailed rules here.\n",
    "prompts": "# Prompts\n\nPut reusable worker prompt templates here.\n",
    "references": "# References\n\nPut optional domain, API, visual style, and example libraries here.\n",
}


def write_placeholder(path: Path, text: str) -> None:
    if not path.exists():
        path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir")
    parser.add_argument("--no-placeholders", action="store_true", help="Create folders only.")
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir)
    skill_dir.mkdir(parents=True, exist_ok=True)

    for folder in ("docs", "prompts", "references", "scripts"):
        target = skill_dir / folder
        target.mkdir(exist_ok=True)
        if folder != "scripts" and not args.no_placeholders:
            write_placeholder(target / ".keep.md", PLACEHOLDERS[folder])

    print(f"Scaffolded layout under {skill_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
