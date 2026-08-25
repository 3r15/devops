#!/usr/bin/env python3
"""PostToolUse hook: keep the generated site honest.

Fires after Write/Edit/Bash. If the tool touched site/, data/curriculum.json or
tools/, re-run the same checks CI runs (scaffold sync, internal links, page
structure) and feed any failure straight back to Claude, so a broken link, a
stale index page, or a colliding progress key is caught at the moment it is
introduced rather than in CI.

Silent when the tool touched nothing relevant, and silent on success.
"""

import json
import pathlib
import subprocess
import sys

REPO = pathlib.Path(__file__).resolve().parent.parent.parent
WATCHED = ("site/", "data/curriculum.json", "tools/")
CHECKS = (
    ["python3", "tools/scaffold.py", "--check"],
    ["python3", "tools/check_links.py"],
    ["python3", "tools/check_structure.py"],
)


def touched(payload: dict) -> bool:
    tool = payload.get("tool_name", "")
    tool_input = payload.get("tool_input") or {}

    if tool == "Bash":
        haystack = tool_input.get("command", "")
    else:
        haystack = str(tool_input.get("file_path", ""))
        response = payload.get("tool_response") or {}
        if isinstance(response, dict):
            haystack += " " + str(response.get("filePath", ""))

    return any(marker in haystack for marker in WATCHED)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    if not touched(payload):
        return 0

    failures = []
    for cmd in CHECKS:
        result = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True)
        if result.returncode != 0:
            failures.append((result.stdout + result.stderr).strip())

    if not failures:
        return 0

    print("사이트 검증 실패 — 커밋 전에 고쳐야 합니다:\n" + "\n\n".join(failures), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
