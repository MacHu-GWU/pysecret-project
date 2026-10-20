#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Check that tests/ mirrors the package per the pywf-oss source-to-test mapping."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKIP_DIRS = {"vendor", "tests", "docs", "__pycache__"}
SKIP_FILES = {"__init__.py", "paths.py", "cli.py"}
RE_PROJECT_NAME = re.compile(r'^name\s*=\s*"([^"]+)"', re.MULTILINE)
RE_COV_CALL = re.compile(
    r"run_cov_test\(\s*(?:script=)?__file__\s*,\s*(?:module=)?[\"']([\w.]+)[\"']",
    re.DOTALL,
)


def find_package_dir(project_root: Path) -> Path | None:
    """Locate the import package: pyproject name first, then a dir with api.py + paths.py."""
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        match = RE_PROJECT_NAME.search(pyproject.read_text(encoding="utf-8"))
        name = match.group(1) if match else ""
        candidate = project_root / name.replace("-", "_")
        if name and (candidate / "__init__.py").exists():
            return candidate
    for child in sorted(project_root.iterdir()):
        if (child / "api.py").exists() and (child / "paths.py").exists():
            return child
    return None


def expected_for_source(package_dir: Path, source: Path) -> tuple[Path, str]:
    """Return (test path relative to project root, dotted module) for one source file."""
    rel = source.resolve().relative_to(package_dir.resolve())
    parts = list(rel.parent.parts)
    stem = rel.stem
    test_name = "test_" + "_".join(parts + [stem]) + ".py"
    test_path = Path("tests", *parts, test_name)
    module = ".".join([package_dir.name] + parts + [stem])
    return test_path, module


def expected_for_folder(package_dir: Path, folder: Path) -> tuple[Path, str]:
    """Return (all.py path relative to project root, dotted module) for one package folder."""
    parts = list(folder.resolve().relative_to(package_dir.resolve()).parts)
    return Path("tests", *parts, "all.py"), ".".join([package_dir.name] + parts)


def iter_sources(package_dir: Path) -> tuple[list[Path], list[Path]]:
    """Return (testable modules, package folders), skipping helper and vendor code."""
    modules: list[Path] = []
    folders: list[Path] = [package_dir]
    stack = [package_dir]
    while stack:
        current = stack.pop()
        for child in sorted(current.iterdir()):
            if child.is_dir():
                if child.name in SKIP_DIRS or not (child / "__init__.py").exists():
                    continue
                folders.append(child)
                stack.append(child)
            elif child.suffix == ".py" and child.name not in SKIP_FILES:
                modules.append(child)
    return modules, folders


def _main(project_root: Path, source: Path | None = None) -> int:
    """Report missing tests, orphan tests, and run_cov_test module mismatches.

    With ``source``, print only the expected test path and module for that file.
    Returns 0 when the layout is clean, 1 when problems are found or input is invalid.
    """
    project_root = project_root.resolve()
    package_dir = find_package_dir(project_root)
    if package_dir is None:
        print(f"ERROR: no package found under {project_root}", file=sys.stderr)
        return 1

    if source is not None:
        source = source if source.is_absolute() else project_root / source
        if source.is_dir():
            test_path, module = expected_for_folder(package_dir, source)
        else:
            test_path, module = expected_for_source(package_dir, source)
        print(f"test file: {test_path}")
        print(f"module:    {module}")
        return 0

    modules, folders = iter_sources(package_dir)
    expected: dict[Path, tuple[str, bool]] = {}
    for module_path in modules:
        test_path, module = expected_for_source(package_dir, module_path)
        expected[test_path] = (module, False)
    for folder in folders:
        test_path, module = expected_for_folder(package_dir, folder)
        expected[test_path] = (module, True)

    missing: list[str] = []
    mismatched: list[str] = []
    for test_path, (module, is_folder) in sorted(expected.items()):
        full = project_root / test_path
        if not full.exists():
            missing.append(f"{test_path}  ->  {module}")
            continue
        text = full.read_text(encoding="utf-8")
        match = RE_COV_CALL.search(text)
        if match is None:
            mismatched.append(
                f'{test_path}: no run_cov_test(__file__, "{module}", ...) block'
            )
        elif match.group(1) != module:
            mismatched.append(
                f"{test_path}: run_cov_test module is {match.group(1)!r}, expected {module!r}"
            )
        elif is_folder and "is_folder=True" not in text:
            mismatched.append(f"{test_path}: all.py must pass is_folder=True")

    orphans: list[str] = []
    tests_dir = project_root / "tests"
    if tests_dir.exists():
        for path in sorted(tests_dir.rglob("*.py")):
            rel = path.relative_to(project_root)
            if "__pycache__" in rel.parts:
                continue
            if (
                path.name.startswith("test_") or path.name == "all.py"
            ) and rel not in expected:
                orphans.append(str(rel))

    for title, items in (
        ("Missing test files", missing),
        ("run_cov_test problems", mismatched),
        ("Orphan test files (map to no module)", orphans),
    ):
        print(f"{title}: {len(items)}")
        for item in items:
            print(f"  {item}")

    return 1 if (missing or mismatched or orphans) else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_test_layout",
        description="Check that tests/ mirrors the package per the pywf-oss mapping rules.",
    )
    parser.add_argument(
        "--project_root",
        type=Path,
        default=Path("."),
        help="repository root (default: .)",
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=None,
        help="only print the expected test path for this source file or folder",
    )
    args = parser.parse_args(argv)
    return _main(project_root=args.project_root, source=args.source)


if __name__ == "__main__":
    sys.exit(main())
