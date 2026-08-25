#!/usr/bin/env python3
"""Structural checks that catch what check_links.py cannot see.

Three failure modes this site is exposed to, all of which ship silently:

  unbalanced tags — a stage page is hand-written HTML; one missing </div>
                    swallows the rest of the page in the browser.
  duplicate progress keys — two stages sharing a data-progress value means
                    one stage's checklist overwrites the other's saved state.
  duplicate checkbox ids — the same id in two places makes labels click the
                    wrong box, and localStorage keys collide.

The last two matter because learner progress lives in localStorage under
those exact strings: a collision silently destroys someone's progress.

Usage:
    python3 tools/check_structure.py
"""

from __future__ import annotations

import collections
import pathlib
import re
import sys
from html.parser import HTMLParser

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

VOID = {
    "area", "base", "br", "col", "embed", "hr", "img",
    "input", "link", "meta", "source", "track", "wbr",
}


class Balance(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list = []
        self.errors: list[str] = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID:
            self.stack.append((tag, self.getpos()))

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if not self.stack:
            self.errors.append(f"line {self.getpos()[0]}: stray </{tag}>")
            return
        top, pos = self.stack.pop()
        if top != tag:
            self.errors.append(
                f"line {self.getpos()[0]}: </{tag}> closes <{top}> opened at line {pos[0]}"
            )


def main() -> int:
    problems: list[str] = []
    pages = sorted(SITE.rglob("*.html"))
    if not pages:
        print("no HTML found under site/", file=sys.stderr)
        return 1

    for page in pages:
        checker = Balance()
        checker.feed(page.read_text(encoding="utf-8"))
        if checker.stack:
            checker.errors.append(
                "never closed: " + ", ".join(f"<{t}> (line {p[0]})" for t, p in checker.stack)
            )
        problems.extend(f"{page.relative_to(ROOT)}: {e}" for e in checker.errors)

    keys: collections.Counter = collections.Counter()
    boxes: collections.Counter = collections.Counter()
    owners: dict = collections.defaultdict(set)

    for page in sorted((SITE / "stages").rglob("*.html")):
        text = page.read_text(encoding="utf-8")
        rel = str(page.relative_to(ROOT))
        for key in re.findall(r'data-progress="([^"]+)"', text):
            keys[key] += 1
            owners[key].add(rel)
        for box in re.findall(r'id="(s\d\d-c\d+)"', text):
            boxes[box] += 1
            owners[box].add(rel)

    for key, count in sorted(keys.items()):
        if count > 1:
            problems.append(
                f'data-progress="{key}" appears {count}x in {", ".join(sorted(owners[key]))} '
                "— learner progress would collide"
            )
    for box, count in sorted(boxes.items()):
        if count > 1:
            problems.append(
                f'checkbox id="{box}" appears {count}x in {", ".join(sorted(owners[box]))}'
            )

    if problems:
        print(f"{len(problems)} structural problem(s):", *problems, sep="\n  ")
        return 1

    print(
        f"ok — {len(pages)} pages, {len(keys)} progress keys, "
        f"{len(boxes)} checkboxes, no collisions"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
