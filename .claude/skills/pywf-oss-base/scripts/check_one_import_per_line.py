#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find, and optionally split, import statements that bring in more than one name."""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

SKIP_PARTS = {"vendor", ".venv", "__pycache__", "build", "dist", ".git"}


def iter_py_files(paths: list[Path]) -> list[Path]:
    """Expand files and folders into .py files, skipping vendored and generated code."""
    files: list[Path] = []
    for path in paths:
        if path.is_file() and path.suffix == ".py":
            files.append(path)
        elif path.is_dir():
            for child in sorted(path.rglob("*.py")):
                if not SKIP_PARTS.intersection(child.parts):
                    files.append(child)
    return files


def alias_text(alias: ast.alias) -> str:
    """Render one imported name, keeping its ``as`` clause."""
    if alias.asname is None:
        return alias.name
    return f"{alias.name} as {alias.asname}"


def split_statement(node: ast.Import | ast.ImportFrom, indent: str) -> list[str]:
    """Return one source line per imported name for a multi-name import."""
    lines: list[str] = []
    for alias in node.names:
        if isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            lines.append(f"{indent}from {module} import {alias_text(alias)}\n")
        else:
            lines.append(f"{indent}import {alias_text(alias)}\n")
    return lines


def find_multi_imports(source: str) -> list[ast.Import | ast.ImportFrom]:
    """Return every import statement that imports more than one name (star imports excluded)."""
    found: list[ast.Import | ast.ImportFrom] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, (ast.Import, ast.ImportFrom)) and len(node.names) > 1:
            found.append(node)
    return sorted(found, key=lambda n: n.lineno)


def _main(paths: list[Path], fix: bool = False) -> int:
    """Report multi-name imports as ``file:line``; with ``fix``, rewrite them one name per line.

    Returns 0 when nothing is left to report, 1 otherwise (including syntax errors).
    """
    remaining = 0
    for path in iter_py_files(paths):
        source = path.read_text(encoding="utf-8")
        try:
            nodes = find_multi_imports(source)
        except SyntaxError as e:
            print(f"ERROR: {path}: {e}", file=sys.stderr)
            remaining += 1
            continue
        if not nodes:
            continue
        if not fix:
            for node in nodes:
                print(
                    f"{path}:{node.lineno}: imports {len(node.names)} names in one statement"
                )
            remaining += len(nodes)
            continue
        lines = source.splitlines(keepends=True)
        # Rewrite from the bottom so earlier line numbers stay valid.
        for node in reversed(nodes):
            block = "".join(lines[node.lineno - 1 : node.end_lineno])
            if "#" in block or ";" in block:
                # A comment or a second statement would be lost; leave it for a human.
                print(
                    f"{path}:{node.lineno}: not fixed (has a comment or ';'), split it by hand"
                )
                remaining += 1
                continue
            first = lines[node.lineno - 1]
            indent = first[: len(first) - len(first.lstrip())]
            lines[node.lineno - 1 : node.end_lineno] = split_statement(node, indent)
        path.write_text("".join(lines), encoding="utf-8")
        print(f"fixed {path}: {len(nodes)} statement(s)")
    return 1 if remaining else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_one_import_per_line",
        description="Find, and optionally split, import statements that bring in more than one name.",
    )
    parser.add_argument(
        "--paths", type=Path, nargs="+", required=True, help="files or folders to check"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="rewrite offending statements, one name per line",
    )
    args = parser.parse_args(argv)
    return _main(paths=args.paths, fix=args.fix)


if __name__ == "__main__":
    sys.exit(main())
