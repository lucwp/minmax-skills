#!/usr/bin/env python3
from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
SKILLS_ROOT = ROOT / "skills"
START = "<!-- SKILL_CATALOG:START -->"
END = "<!-- SKILL_CATALOG:END -->"

CATEGORY_NAMES = {
    "orchestration-agents": "Orchestration & Agents",
    "business-revenue": "Business & Revenue",
    "product-growth": "Product & Growth",
    "marketing-content": "Marketing & Content",
    "design-ux": "Design & UX",
    "operations-process": "Operations & Process",
    "data-analytics": "Data & Analytics",
    "career": "Career",
    "artifact-workflows": "Artifact Workflows",
}


def parse_skill(path: Path) -> tuple[str, str]:
    text = path.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+?)\s*$", text, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else path.parent.name.replace("-", " ").title()

    description = ""
    frontmatter = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if frontmatter:
        desc_match = re.search(r"^description:\s*[\"']?(.+?)[\"']?\s*$", frontmatter.group(1), re.MULTILINE)
        if desc_match:
            description = desc_match.group(1).strip()

    if not description:
        body = re.sub(r"^#\s+.+?$", "", text, count=1, flags=re.MULTILINE).strip()
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", body) if p.strip()]
        for paragraph in paragraphs:
            if paragraph.startswith("**Author:**"):
                continue
            if paragraph.startswith("#"):
                continue
            description = " ".join(line.strip() for line in paragraph.splitlines())
            break

    description = re.sub(r"\s+", " ", description).strip()
    if len(description) > 180:
        description = description[:177].rstrip() + "..."
    return title, description or "Reusable agent skill."


def build_catalog() -> str:
    grouped: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for skill_file in sorted(SKILLS_ROOT.glob("*/*/SKILL.md")):
        category = skill_file.parent.parent.name
        title, description = parse_skill(skill_file)
        rel_dir = skill_file.parent.relative_to(ROOT).as_posix() + "/"
        grouped[category].append((title, description, rel_dir))

    count = sum(len(items) for items in grouped.values())
    category_count = sum(1 for items in grouped.values() if items)
    skill_word = "skill" if count == 1 else "skills"
    category_word = "category" if category_count == 1 else "categories"

    lines = [START, "## Skill catalog", "", f"**{count} public {skill_word}** across **{category_count} {category_word}**.", ""]
    ordered_categories = list(CATEGORY_NAMES) + sorted(set(grouped) - set(CATEGORY_NAMES))
    for category in ordered_categories:
        items = grouped.get(category)
        if not items:
            continue
        lines += [f"### {CATEGORY_NAMES.get(category, category.replace('-', ' ').title())}", "", "| Skill | What it does |", "| --- | --- |"]
        for title, description, rel_dir in sorted(items, key=lambda item: item[0].lower()):
            safe_description = description.replace("|", "\\|")
            lines.append(f"| [{title}]({rel_dir}) | {safe_description} |")
        lines.append("")
    lines.append(END)
    return "\n".join(lines)


def main() -> None:
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit("README catalog markers not found")
    before, rest = text.split(START, 1)
    _, after = rest.split(END, 1)
    README.write_text(before.rstrip() + "\n\n" + build_catalog() + after, encoding="utf-8")


if __name__ == "__main__":
    main()
