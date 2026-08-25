#!/usr/bin/env python3
"""Verify that every internal link and asset reference in site/ resolves.

Catches the failure mode this site is most exposed to: a hand-written stage
page pointing at a path that only exists in someone's head. External links
(http/https), mailto:, data: and pure fragments are skipped.

Usage:
    python3 tools/check_links.py
"""

from __future__ import annotations

import pathlib
import re
import sys
from urllib.parse import unquote, urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

REF_RE = re.compile(r'(?:href|src)\s*=\s*"([^"]+)"', re.IGNORECASE)
SKIP_SCHEMES = ("http:", "https:", "mailto:", "data:", "javascript:", "tel:")


def main() -> int:
    problems: list[str] = []
    pages = sorted(SITE.rglob("*.html"))
    if not pages:
        print("no HTML found under site/", file=sys.stderr)
        return 1

    checked = 0
    for page in pages:
        html = page.read_text(encoding="utf-8")
        ids = set(re.findall(r'id\s*=\s*"([^"]+)"', html))

        for raw in REF_RE.findall(html):
            ref = raw.strip()
            if not ref or ref.lower().startswith(SKIP_SCHEMES) or ref.startswith("//"):
                continue

            if ref.startswith("#"):
                checked += 1
                if ref[1:] and ref[1:] not in ids:
                    problems.append(f"{page.relative_to(ROOT)} -> {ref} (no such id on this page)")
                continue

            parsed = urlparse(ref)
            target_path = unquote(parsed.path)
            if not target_path:
                continue

            checked += 1
            target = (page.parent / target_path).resolve()
            if not target.exists():
                problems.append(f"{page.relative_to(ROOT)} -> {ref} (missing file)")
                continue

            if parsed.fragment and target.suffix == ".html":
                target_ids = set(
                    re.findall(r'id\s*=\s*"([^"]+)"', target.read_text(encoding="utf-8"))
                )
                if parsed.fragment not in target_ids:
                    problems.append(
                        f"{page.relative_to(ROOT)} -> {ref} (no id '{parsed.fragment}' in target)"
                    )

    if problems:
        print(f"{len(problems)} broken reference(s):", *problems, sep="\n  ")
        return 1

    print(f"ok — {checked} internal references across {len(pages)} pages resolve")
    return 0


if __name__ == "__main__":
    sys.exit(main())
