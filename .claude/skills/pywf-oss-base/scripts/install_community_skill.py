#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stage and install a community Agent Skill from its pinned GitHub tree URL in the catalog."""

from __future__ import annotations

import argparse
import datetime
import json
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib
import urllib.request
from pathlib import Path

DEFAULT_CATALOG = (
    Path(__file__).resolve().parent.parent / "assets" / "community-skills.toml"
)
RE_TREE_URL = re.compile(
    r"^https://github\.com/(?P<owner>[^/]+)/(?P<repo>[^/]+)/tree/(?P<ref>[0-9a-f]{40})/(?P<path>.+?)/?$"
)
RE_NAME = re.compile(r"^name:\s*['\"]?([^'\"\n]+?)['\"]?\s*$", re.MULTILINE)
SCRIPT_SUFFIXES = {".py", ".sh", ".bash", ".js", ".mjs", ".ts", ".rb", ".pl", ".ps1"}


def load_catalog(catalog: Path) -> list[dict]:
    """Return the [[skill]] entries of the catalog."""
    with catalog.open("rb") as f:
        return tomllib.load(f).get("skill", [])


def parse_tree_url(url: str) -> dict[str, str]:
    """Split a pinned tree URL into owner, repo, ref (40-char sha), and path."""
    match = RE_TREE_URL.match(url)
    if match is None:
        raise ValueError(
            f"not a pinned tree URL (https://github.com/<owner>/<repo>/tree/<40-char sha>/<path>): {url}"
        )
    return match.groupdict()


def download_folder(parts: dict[str, str], staging: Path) -> None:
    """Download the repo tarball at the pinned commit and extract only the skill folder into staging."""
    tarball_url = f"https://codeload.github.com/{parts['owner']}/{parts['repo']}/tar.gz/{parts['ref']}"
    with tempfile.TemporaryDirectory() as tmp:
        tar_path = Path(tmp) / "repo.tar.gz"
        with (
            urllib.request.urlopen(tarball_url, timeout=120) as response,
            tar_path.open("wb") as f,
        ):
            shutil.copyfileobj(response, f)
        with tarfile.open(tar_path, "r:gz") as tar:
            members = tar.getmembers()
            if not members:
                raise ValueError("empty tarball")
            root = members[0].name.split("/", 1)[0]
            prefix = f"{root}/{parts['path'].strip('/')}/"
            picked = 0
            for member in members:
                if not member.name.startswith(prefix) or member.name == prefix.rstrip(
                    "/"
                ):
                    continue
                rel = Path(member.name[len(prefix) :])
                if rel.is_absolute() or ".." in rel.parts:
                    raise ValueError(f"unsafe path in tarball: {member.name}")
                if member.issym() or member.islnk():
                    print(f"skipped link: {rel}", file=sys.stderr)
                    continue
                target = staging / rel
                if member.isdir():
                    target.mkdir(parents=True, exist_ok=True)
                elif member.isfile():
                    target.parent.mkdir(parents=True, exist_ok=True)
                    source = tar.extractfile(member)
                    if source is None:
                        continue
                    with source, target.open("wb") as out:
                        shutil.copyfileobj(source, out)
                    picked += 1
            if picked == 0:
                raise ValueError(f"path not found at this commit: {parts['path']}")


def summarize(staging: Path) -> None:
    """Print what would be installed, with executable scripts called out for review."""
    files = sorted(p for p in staging.rglob("*") if p.is_file())
    scripts = [p for p in files if p.suffix in SCRIPT_SUFFIXES]
    total = sum(p.stat().st_size for p in files)
    print(f"staged {len(files)} files ({total / 1024:.0f} KiB) in {staging}")
    print("top level:")
    for child in sorted(staging.iterdir()):
        print(f"  {child.name}{'/' if child.is_dir() else ''}")
    print(f"scripts to review ({len(scripts)}):")
    for script in scripts:
        print(f"  {script.relative_to(staging)}")


def _main(
    project_root: Path,
    name: str | None = None,
    catalog: Path = DEFAULT_CATALOG,
    list_only: bool = False,
    install: bool = False,
    force: bool = False,
) -> int:
    """List the catalog, or stage a skill into tmp/ for review, and with ``install`` copy it into .claude/skills/.

    Returns 0 on success, 1 on any failure.
    """
    entries = load_catalog(catalog)
    if list_only:
        for entry in entries:
            parts = parse_tree_url(entry["url"])
            print(
                f"{entry['name']}: {parts['owner']}/{parts['repo']} @ {parts['ref'][:7]} / {parts['path']} ({entry.get('license', '?')})"
            )
            print(f"  when to use: {entry.get('when_to_use', '')}")
        return 0
    matches = [e for e in entries if e.get("name") == name]
    if not matches:
        print(f"ERROR: no skill named {name!r} in {catalog}", file=sys.stderr)
        return 1
    entry = matches[0]
    try:
        parts = parse_tree_url(entry["url"])
    except ValueError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    project_root = project_root.resolve()
    dest = project_root / ".claude" / "skills" / name
    if install and dest.exists() and not force:
        print(
            f"ERROR: {dest} already exists; rerun with --force to replace it",
            file=sys.stderr,
        )
        return 1
    staging = project_root / "tmp" / "community-skills" / f"{name}@{parts['ref'][:7]}"
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)
    try:
        download_folder(parts, staging)
    except (OSError, ValueError, tarfile.TarError) as e:
        print(f"ERROR: download failed: {e}", file=sys.stderr)
        return 1

    skill_md = staging / "SKILL.md"
    if not skill_md.exists():
        print(f"ERROR: no SKILL.md at {parts['path']}", file=sys.stderr)
        return 1
    found = RE_NAME.search(skill_md.read_text(encoding="utf-8"))
    if found is None or found.group(1) != name:
        print(
            f"ERROR: SKILL.md name is {found.group(1) if found else None!r}, catalog says {name!r}",
            file=sys.stderr,
        )
        return 1
    summarize(staging)
    if not install:
        print("not installed: review the staged files, then rerun with --install")
        return 0

    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(staging, dest)
    source = {
        "name": name,
        "url": entry["url"],
        "license": entry.get("license"),
        "installed_on": datetime.date.today().isoformat(),
    }
    (dest / ".source.json").write_text(
        json.dumps(source, indent=2) + "\n", encoding="utf-8"
    )
    shutil.rmtree(staging)
    print(f"installed {name} into {dest}")
    ignored = subprocess.run(
        ["git", "check-ignore", "-q", str(dest / "SKILL.md")],
        cwd=project_root,
        capture_output=True,
    )
    if ignored.returncode == 0:
        print(
            f"git: .claude/skills/{name}/ is git-ignored (default); delete its line in .gitignore to commit it"
        )
    elif ignored.returncode == 1:
        print(
            f"git: .claude/skills/{name}/ is NOT git-ignored; add its line to the community-skills block of .gitignore, or commit it on purpose"
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="install_community_skill",
        description="Stage and install a community Agent Skill from its pinned GitHub tree URL in the catalog.",
    )
    parser.add_argument("--name", default=None, help="skill name in the catalog")
    parser.add_argument(
        "--list",
        dest="list_only",
        action="store_true",
        help="list the catalog and exit",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="copy the staged skill into .claude/skills/",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="replace an installed skill of the same name",
    )
    parser.add_argument(
        "--project_root",
        type=Path,
        default=Path("."),
        help="repository root (default: .)",
    )
    parser.add_argument(
        "--catalog",
        type=Path,
        default=DEFAULT_CATALOG,
        help="catalog TOML (default: the base skill's assets)",
    )
    args = parser.parse_args(argv)
    if not args.list_only and not args.name:
        parser.error("--name is required unless --list is given")
    return _main(
        project_root=args.project_root,
        name=args.name,
        catalog=args.catalog,
        list_only=args.list_only,
        install=args.install,
        force=args.force,
    )


if __name__ == "__main__":
    sys.exit(main())
