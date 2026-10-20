#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check a base + invoker skill family against the rules in 00-authoring-references.md."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RE_FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.DOTALL)
RE_REF_CITE = re.compile(r"(?<![\w-])(\d{2})-[a-z0-9-]+\.md")
RE_FENCE = re.compile(r"^(```|~~~)")
SCANNED_SUFFIXES = {".md", ".py", ".json", ".ipynb"}


def frontmatter(text: str) -> str | None:
    """Return the YAML frontmatter body, or None when the file has none."""
    match = RE_FRONTMATTER.match(text)
    return match.group(1) if match else None


def field(fm: str, name: str) -> str | None:
    """Return the raw value of a top-level frontmatter field."""
    match = re.search(rf"^{name}:\s*(.*)$", fm, re.MULTILINE)
    return match.group(1).strip() if match else None


def is_double_quoted(value: str | None) -> bool:
    """True for a single double-quoted string with no inner double quotes."""
    return (
        bool(value)
        and value.startswith('"')
        and value.endswith('"')
        and value.count('"') == 2
    )


def count_h1(text: str) -> int:
    """Count level-1 Markdown headings outside fenced code blocks."""
    in_fence = False
    count = 0
    for line in text.splitlines():
        if RE_FENCE.match(line.strip()):
            in_fence = not in_fence
        elif not in_fence and line.startswith("# "):
            count += 1
    return count


def check_skills(skills_dir: Path, prefix: str, errors: list[str]) -> None:
    """Frontmatter of every SKILL.md, and every ../<prefix>-base/... path an invoker cites."""
    re_base_path = re.compile(rf"\.\./{re.escape(prefix)}-base/[A-Za-z0-9_./*-]+")
    for skill in sorted(skills_dir.glob(f"{prefix}-*")):
        skill_md = skill / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"{skill.name}: missing SKILL.md")
            continue
        text = skill_md.read_text(encoding="utf-8")
        fm = frontmatter(text)
        if fm is None:
            errors.append(f"{skill_md}: no frontmatter")
            continue
        if field(fm, "name") != skill.name:
            errors.append(
                f"{skill_md}: name is {field(fm, 'name')!r}, expected {skill.name!r}"
            )
        if not is_double_quoted(field(fm, "description")):
            errors.append(f"{skill_md}: description must be one double-quoted string")
        if field(fm, "disable-model-invocation") is not None:
            errors.append(
                f"{skill_md}: skills are model-invocable; remove disable-model-invocation"
            )
        for raw in sorted(set(re_base_path.findall(text))):
            rel = raw.rstrip(".,)")
            if "*" in rel:
                found = list(skill.glob(rel))
            else:
                found = [skill / rel] if (skill / rel).exists() else []
            if not found:
                errors.append(f"{skill_md}: path does not resolve: {rel}")


def check_references(skills_dir: Path, prefix: str, errors: list[str]) -> None:
    """Reference shape, cited references exist, and no reference cites a later one."""
    ref_dir = skills_dir / f"{prefix}-base" / "references"
    existing = {p.name for p in ref_dir.glob("*.md")}
    for path in sorted(skills_dir.glob(f"{prefix}-*/**/*.md")):
        text = path.read_text(encoding="utf-8")
        is_reference = path.parent == ref_dir
        if is_reference:
            fm = frontmatter(text)
            if fm is None or not is_double_quoted(field(fm, "description")):
                errors.append(
                    f"{path.name}: needs frontmatter with one double-quoted description"
                )
            if count_h1(text) != 1:
                errors.append(
                    f"{path.name}: needs exactly one H1, found {count_h1(text)}"
                )
        own = path.name[:2] if is_reference else None
        for match in RE_REF_CITE.finditer(text):
            cited = match.group(0)
            if cited not in existing:
                errors.append(
                    f"{path.relative_to(skills_dir)}: cites missing reference {cited}"
                )
                continue
            if own is not None and cited[:2] > own:
                errors.append(
                    f"{path.name}: cites later reference {cited} (cite backward only)"
                )


def check_forbidden(
    skills_dir: Path, prefix: str, forbid: list[str], errors: list[str]
) -> None:
    """No project-specific name appears anywhere in the family."""
    if not forbid:
        return
    for path in sorted(skills_dir.glob(f"{prefix}-*/**/*")):
        if not path.is_file() or path.suffix not in SCANNED_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8")
        for name in forbid:
            if name in text:
                line_no = text[: text.index(name)].count("\n") + 1
                errors.append(
                    f"{path.relative_to(skills_dir)}:{line_no}: forbidden name {name!r}"
                )


def _main(
    skills_dir: Path, prefix: str = "pywf-oss", forbid: list[str] | None = None
) -> int:
    """Run every check and print one line per problem.

    Returns 0 when the family is consistent, 1 when any problem is found.
    """
    if not (skills_dir / f"{prefix}-base").is_dir():
        print(f"ERROR: {skills_dir}/{prefix}-base not found", file=sys.stderr)
        return 1
    errors: list[str] = []
    check_skills(skills_dir, prefix, errors)
    check_references(skills_dir, prefix, errors)
    check_forbidden(skills_dir, prefix, forbid or [], errors)
    for error in errors:
        print(error)
    print(f"{len(errors)} problem(s)")
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_skill_family",
        description="Check a base + invoker skill family against its authoring rules.",
    )
    parser.add_argument(
        "--skills_dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent.parent,
        help="folder holding the skills (default: the folder that holds this script's skill)",
    )
    parser.add_argument(
        "--prefix", default="pywf-oss", help="skill family prefix (default: pywf-oss)"
    )
    parser.add_argument(
        "--forbid",
        action="append",
        default=[],
        help="a project-specific name that must not appear; repeat for several",
    )
    args = parser.parse_args(argv)
    return _main(skills_dir=args.skills_dir, prefix=args.prefix, forbid=args.forbid)


if __name__ == "__main__":
    sys.exit(main())
