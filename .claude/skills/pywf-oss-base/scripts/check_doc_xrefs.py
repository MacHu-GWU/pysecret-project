#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Find Sphinx cross-references that rendered as plain code instead of links."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RE_XREF = re.compile(r'<code class="xref[^"]*"[^>]*>(.*?)</code>', re.DOTALL)
RE_LINK_OPEN = re.compile(r"<a [^>]*>\s*$")
RE_TAG = re.compile(r"<[^>]+>")
SKIP_PARTS = {"_static", "_sources", "_modules", "_images"}
SKIP_NAMES = {"genindex.html", "search.html", "py-modindex.html"}


def page_body(html: str) -> str:
    """Return the main article of a furo page, or the whole page for other themes."""
    start = html.find("<article")
    end = html.find("</article>")
    if start == -1 or end == -1:
        return html
    return html[start:end]


def unresolved_xrefs(html: str) -> tuple[int, list[str]]:
    """Return (number of xrefs, texts of xrefs that are not wrapped in a link)."""
    body = page_body(html)
    total = 0
    bad: list[str] = []
    for match in RE_XREF.finditer(body):
        total += 1
        before = body[max(0, match.start() - 400) : match.start()]
        if RE_LINK_OPEN.search(before) is None:
            bad.append(RE_TAG.sub("", match.group(1)).strip())
    return total, bad


def iter_pages(html_dir: Path, include_api: bool) -> list[Path]:
    """List the HTML pages to scan, skipping Sphinx's generated index and asset pages."""
    pages: list[Path] = []
    for path in sorted(html_dir.rglob("*.html")):
        rel = path.relative_to(html_dir)
        if SKIP_PARTS.intersection(rel.parts) or rel.name in SKIP_NAMES:
            continue
        if not include_api and rel.parts[0] == "api":
            continue
        pages.append(path)
    return pages


def _main(html_dir: Path, include_api: bool = False) -> int:
    """Report every unresolved cross-reference per page of a built Sphinx site.

    Sphinx does not warn when a ``:class:`` / ``:func:`` / ``:attr:`` target is
    missing (unless nitpicky mode is on); the reference silently renders as code.
    Returns 0 when all references resolve, 1 when any do not or the input is invalid.
    """
    if not html_dir.is_dir():
        print(
            f"ERROR: {html_dir} is not a directory; run `mise run build-doc` first",
            file=sys.stderr,
        )
        return 1
    pages = iter_pages(html_dir, include_api)
    grand_total = 0
    grand_bad = 0
    for page in pages:
        total, bad = unresolved_xrefs(page.read_text(encoding="utf-8"))
        grand_total += total
        grand_bad += len(bad)
        for text in bad:
            print(f"{page.relative_to(html_dir)}: unresolved {text}")
    print(
        f"Scanned {len(pages)} pages, {grand_total} cross-references, {grand_bad} unresolved"
    )
    return 1 if grand_bad else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="check_doc_xrefs",
        description="Find Sphinx cross-references that rendered as plain code instead of links.",
    )
    parser.add_argument(
        "--html_dir",
        type=Path,
        default=Path("docs/build/html"),
        help="built HTML folder (default: docs/build/html)",
    )
    parser.add_argument(
        "--include_api",
        action="store_true",
        help="also scan the generated API pages (type hints there may not resolve)",
    )
    args = parser.parse_args(argv)
    return _main(html_dir=args.html_dir, include_api=args.include_api)


if __name__ == "__main__":
    sys.exit(main())
