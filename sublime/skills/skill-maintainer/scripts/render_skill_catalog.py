#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path


TIER_INFO = {
    "promoted": "Recommended first-choice entrypoints. Route here first unless a narrower owner is already obvious.",
    "supported": "Stable specialized skills. Use when the task clearly matches the owned area.",
    "in-progress": "Useful but still evolving in coverage, prompts, scripts, or naming. Use deliberately and expect refinement.",
    "deprecated": "Kept only for compatibility or archival reference. Avoid for new workflows.",
}

DOMAIN_INFO = {
    "repo-operations": "Skill routing, maintenance, handoff, git, and release operations.",
    "qt-desktop": "Generic Qt/C++ desktop engineering, review, threading, UI, and ownership work.",
    "mobiletrans": "MobileTrans product-specific Qt/Desktop workflows and bug domains.",
    "blueking-ops": "BlueKing DevOps, issue, and OpenSpec-linked work-item operations.",
    "spec-and-process": "Persistent specs, project bootstrap, and process-oriented engineering docs.",
    "artifact-generation": "HTML/PDF/report-oriented artifact generation and visualization helpers.",
    "analysis-and-guidance": "Log analysis, grilling, and investigation-oriented guidance skills.",
    "workspace-integration": "External workspace or SaaS integration automation.",
}


@dataclass
class SkillRow:
    name: str
    tier: str
    domain: str
    entrypoint: bool
    description: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the official tier/domain catalog for a local Codex skills repo.")
    parser.add_argument("root", help="Skills root")
    parser.add_argument("--catalog", required=True, help="CSV source of truth for tier/domain buckets")
    parser.add_argument("--out", required=True, help="Markdown output path")
    return parser.parse_args()


def parse_bool(value: str) -> bool:
    return value.strip().lower() in {"1", "true", "yes", "y"}


def extract_description(skill_dir: Path) -> str:
    path = skill_dir / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""

    collecting = False
    parts: list[str] = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if collecting:
            if line.startswith(" ") or line.startswith("\t"):
                parts.append(line.strip())
                continue
            break
        if not line.startswith("description:"):
            continue
        rest = line.split(":", 1)[1].strip()
        if rest in {">", "|"}:
            collecting = True
            continue
        return " ".join(rest.strip("'\"").split())

    return " ".join(" ".join(parts).split())


def load_rows(root: Path, catalog_path: Path) -> list[SkillRow]:
    skills = sorted([p for p in root.iterdir() if p.is_dir() and (p / "SKILL.md").exists()], key=lambda p: p.name)
    skill_names = {skill.name for skill in skills}

    rows: list[SkillRow] = []
    seen: set[str] = set()
    with catalog_path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for raw in reader:
            name = raw["name"].strip()
            if name in seen:
                raise ValueError(f"Duplicate skill in catalog: {name}")
            seen.add(name)
            tier = raw["tier"].strip()
            domain = raw["domain"].strip()
            if tier not in TIER_INFO:
                raise ValueError(f"Unknown tier for {name}: {tier}")
            if domain not in DOMAIN_INFO:
                raise ValueError(f"Unknown domain for {name}: {domain}")
            rows.append(
                SkillRow(
                    name=name,
                    tier=tier,
                    domain=domain,
                    entrypoint=parse_bool(raw["entrypoint"]),
                    description=extract_description(root / name),
                )
            )

    catalog_names = {row.name for row in rows}
    missing = sorted(skill_names - catalog_names)
    extra = sorted(catalog_names - skill_names)
    if missing or extra:
        problems: list[str] = []
        if missing:
            problems.append(f"missing from catalog: {', '.join(missing)}")
        if extra:
            problems.append(f"not found on disk: {', '.join(extra)}")
        raise ValueError("Catalog mismatch: " + "; ".join(problems))

    return rows


def render(root: Path, rows: list[SkillRow], catalog_path: Path) -> str:
    by_tier: dict[str, list[SkillRow]] = defaultdict(list)
    by_domain: dict[str, list[SkillRow]] = defaultdict(list)
    entrypoints: dict[str, list[SkillRow]] = defaultdict(list)

    for row in rows:
        by_tier[row.tier].append(row)
        by_domain[row.domain].append(row)
        if row.entrypoint:
            entrypoints[row.domain].append(row)

    lines: list[str] = []
    lines.append("# Skills Catalog")
    lines.append("")
    lines.append(f"Generated on {date.today().isoformat()} from `{root}` using `{catalog_path.name}`.")
    lines.append("")
    lines.append("## Purpose")
    lines.append("")
    lines.append("- `SKILLS-CATALOG.csv` is the source of truth for release tiers and formal business-domain buckets.")
    lines.append("- `SKILLS-CATALOG.md` is the official routing view for humans.")
    lines.append("- Keep active skill folders in place. Use these buckets for discovery and maintenance, not automatic path moves.")
    lines.append("")
    lines.append("## Release Tiers")
    lines.append("")

    for tier in ("promoted", "supported", "in-progress", "deprecated"):
        lines.append(f"### {tier}")
        lines.append("")
        lines.append(TIER_INFO[tier])
        lines.append("")

    lines.append("## Domain Buckets")
    lines.append("")
    for domain in DOMAIN_INFO:
        lines.append(f"### {domain}")
        lines.append("")
        lines.append(DOMAIN_INFO[domain])
        lines.append("")

    lines.append("## Default Entry Points")
    lines.append("")
    for domain in DOMAIN_INFO:
        items = sorted(entrypoints.get(domain, []), key=lambda row: (row.tier != "promoted", row.name))
        lines.append(f"### {domain}")
        lines.append("")
        if not items:
            lines.append("- None")
        else:
            for row in items:
                lines.append(f"- `{row.name}` ({row.tier})")
        lines.append("")

    lines.append("## By Tier")
    lines.append("")
    for tier in ("promoted", "supported", "in-progress", "deprecated"):
        items = sorted(by_tier.get(tier, []), key=lambda row: row.name)
        lines.append(f"### {tier} ({len(items)})")
        lines.append("")
        if not items:
            lines.append("- None")
        else:
            for row in items:
                markers = [row.domain]
                if row.entrypoint:
                    markers.append("entrypoint")
                suffix = f" [{' | '.join(markers)}]" if markers else ""
                lines.append(f"- `{row.name}`{suffix}: {row.description}")
        lines.append("")

    lines.append("## By Domain")
    lines.append("")
    for domain in DOMAIN_INFO:
        items = sorted(by_domain.get(domain, []), key=lambda row: (row.tier != "promoted", row.name))
        lines.append(f"### {domain} ({len(items)})")
        lines.append("")
        if not items:
            lines.append("- None")
        else:
            for row in items:
                markers = [row.tier]
                if row.entrypoint:
                    markers.append("entrypoint")
                lines.append(f"- `{row.name}` [{' | '.join(markers)}]: {row.description}")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    root = Path(args.root)
    catalog_path = Path(args.catalog)
    output_path = Path(args.out)
    rows = load_rows(root, catalog_path)
    output_path.write_text(render(root, rows, catalog_path), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
