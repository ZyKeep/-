#!/usr/bin/env python3
"""Audit Codex skill folders and report token-heavy candidates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def count_lines(text: str) -> int:
    return 0 if not text else text.count("\n") + 1


def priority(size_kb: float, lines: int, scripts: int, refs: int) -> str:
    if size_kb >= 10 and scripts == 0 and refs == 0:
        return "high"
    if size_kb >= 10:
        return "medium"
    if lines >= 180 and scripts == 0 and refs == 0:
        return "medium"
    return "low"


def recommendation(size_kb: float, lines: int, scripts: int, refs: int) -> str:
    if size_kb >= 10 and scripts == 0 and refs == 0:
        return "Split long sections into references; add scripts for repeated searches or report generation."
    if size_kb >= 10 and refs > 0:
        return "Trim SKILL.md further; keep only routing and load references on demand."
    if lines >= 180 and scripts == 0:
        return "Review for repeated commands that can become scripts."
    return "Keep as is unless real usage shows repeated manual work."


def audit_skill(path: Path) -> dict[str, object] | None:
    skill_md = path / "SKILL.md"
    if not skill_md.exists():
        return None
    text = skill_md.read_text(encoding="utf-8", errors="replace")
    scripts_dir = path / "scripts"
    refs_dir = path / "references"
    script_count = len([p for p in scripts_dir.rglob("*") if p.is_file()]) if scripts_dir.exists() else 0
    ref_count = len([p for p in refs_dir.rglob("*") if p.is_file()]) if refs_dir.exists() else 0
    size_kb = skill_md.stat().st_size / 1024
    lines = count_lines(text)
    return {
        "name": path.name,
        "path": str(path),
        "skill_md_kb": round(size_kb, 1),
        "lines": lines,
        "scripts": script_count,
        "references": ref_count,
        "priority": priority(size_kb, lines, script_count, ref_count),
        "recommendation": recommendation(size_kb, lines, script_count, ref_count),
    }


def write_markdown(rows: list[dict[str, object]], out: Path) -> None:
    totals = {
        "skills": len(rows),
        "high": sum(1 for r in rows if r["priority"] == "high"),
        "medium": sum(1 for r in rows if r["priority"] == "medium"),
    }
    lines = [
        "# Skill Audit Report",
        "",
        f"- Skills scanned: {totals['skills']}",
        f"- High priority: {totals['high']}",
        f"- Medium priority: {totals['medium']}",
        "",
        "| Priority | Skill | KB | Lines | Scripts | References | Recommendation |",
        "| --- | --- | ---: | ---: | ---: | ---: | --- |",
    ]
    for r in rows:
        lines.append(
            f"| {r['priority']} | `{r['name']}` | {r['skill_md_kb']} | {r['lines']} | "
            f"{r['scripts']} | {r['references']} | {r['recommendation']} |"
        )
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=r"C:\Users\ws\.codex\skills")
    parser.add_argument("--out", help="Write a Markdown report to this path.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of a compact table.")
    args = parser.parse_args()

    root = Path(args.root)
    rows = [r for p in sorted(root.iterdir()) if p.is_dir() for r in [audit_skill(p)] if r]
    rows.sort(key=lambda r: ({"high": 0, "medium": 1, "low": 2}[str(r["priority"])], -float(r["skill_md_kb"])))

    if args.out:
        write_markdown(rows, Path(args.out))

    if args.json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
    else:
        for r in rows[:20]:
            print(f"{r['priority']:6} {r['skill_md_kb']:>5}KB {r['lines']:>4} lines  {r['name']}  scripts={r['scripts']} refs={r['references']}")
        if len(rows) > 20:
            print(f"... {len(rows) - 20} more skills omitted; use --out or --json for full output")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

