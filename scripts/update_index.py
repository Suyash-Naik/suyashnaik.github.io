"""Regenerate the 'Recent work' teasers in index.qmd from projects.yaml.

Usage: pixi run update-index
"""

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PROJECTS_YAML = ROOT / "projects.yaml"
INDEX_QMD = ROOT / "index.qmd"

START_MARKER = "<!-- PROJECTS:START -->"
END_MARKER = "<!-- PROJECTS:END -->"


def render_stats(stats):
    lines = ["::: {.project-stats}"]
    for stat in stats:
        lines.append(f"[{stat['value']}]{{.ps-value}} [{stat['label']}]{{.ps-label}}")
    lines.append(":::")
    return "\n".join(lines)


def render_teaser(project):
    return "\n".join(
        [
            "::: {.project-teaser}",
            f"### [{project['title']}]({project['link']})",
            project["blurb"].strip(),
            "",
            render_stats(project.get("stats", [])),
            "",
            f"[Full case study →]({project['link']}){{.project-case-link}}",
            ":::",
        ]
    )


def render_block(projects):
    featured = sorted(
        (p for p in projects if p.get("featured")),
        key=lambda p: p.get("order", 999),
    )

    blocks = [render_teaser(p) for p in featured]
    blocks.append('::: {.project-teaser}\n### [Incoming]\n:::')

    return "\n\n\n".join(blocks) + "\n\n[All projects →](projects/index.qmd)"


def main():
    data = yaml.safe_load(PROJECTS_YAML.read_text(encoding="utf-8"))
    new_block = render_block(data.get("projects", []))

    original = INDEX_QMD.read_text(encoding="utf-8")
    if START_MARKER not in original or END_MARKER not in original:
        print(f"error: {INDEX_QMD} is missing {START_MARKER} / {END_MARKER} markers", file=sys.stderr)
        return 1

    before, rest = original.split(START_MARKER, 1)
    _, after = rest.split(END_MARKER, 1)
    updated = f"{before}{START_MARKER}\n{new_block}\n{END_MARKER}{after}"

    if updated == original:
        print("index.qmd already up to date")
        return 0

    INDEX_QMD.write_text(updated, encoding="utf-8")
    print("index.qmd updated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
