#!/usr/bin/env python3
"""Generate the DevOps Learning Path site scaffolding from data/curriculum.json.

Two kinds of pages live in site/:

  derived  — index.html and parts/<slug>/index.html are pure functions of
             curriculum.json and are rewritten on every run.
  authored — stages/<nn>-<slug>/index.html holds hand-written lesson content.
             It is only created when missing, so running this tool never eats
             work. Resetting one back to a stub takes --force --stage N.

Usage:
    python3 tools/scaffold.py                    # refresh derived pages, add new stubs
    python3 tools/scaffold.py --check            # fail if derived pages are stale
    python3 tools/scaffold.py --force --stage 2  # reset ONE stage page back to a stub

--force discards hand-written lesson content, so it refuses to run without --stage:
a bare --force would silently blank every stage already published.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "curriculum.json"
SITE = ROOT / "site"

STATUS_LABEL = {"planned": ("", "예정"), "wip": ("wip", "작성 중"), "done": ("done", "완료")}


def esc(text: str) -> str:
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def stage_dir(stage: dict) -> str:
    return f"{stage['n']:02d}-{stage['slug']}"


def status_badge(stage: dict) -> str:
    cls, label = STATUS_LABEL.get(stage["status"], ("", stage["status"]))
    attr = f"badge {cls}".strip()
    return f'<span class="{attr}">{label}</span>'


def shell(title: str, description: str, depth: int, body: str) -> str:
    """Wrap page body in the shared chrome. `depth` = directories below site/."""
    up = "../" * depth
    nav = [
        ("커리큘럼", f"{up}index.html#parts", False),
        ("학습 계획", f"{up}plan.html", False),
        ("소개", f"{up}about.html", True),
        ("GitHub", "https://github.com/3r15/devops", True),
    ]
    nav_html = "\n".join(
        '      <a href="{href}"{cls}>{label}</a>'.format(
            href=href, label=label, cls=' class="hide-sm"' if small else ""
        )
        for label, href, small in nav
    )
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>🛠️</text></svg>">
<link rel="stylesheet" href="{up}assets/css/main.css">
<script src="{up}assets/js/theme-init.js"></script>
</head>
<body>
<header class="site-header">
  <div class="wrap">
    <a class="brand" href="{up}index.html">DevOps<span class="dot">::</span>Path</a>
    <nav class="site-nav">
{nav_html}
      <button class="theme-toggle" data-theme-toggle type="button" aria-label="테마 전환">☾</button>
    </nav>
  </div>
</header>

<main>
  <div class="wrap">
{body}
  </div>
</main>

<footer class="site-footer">
  <div class="wrap">
    <span>DevOps Learning Path — 14 stages, 5 parts</span>
    <span>Built with GitHub Pages</span>
  </div>
</footer>

<script src="{up}assets/js/main.js"></script>
</body>
</html>
"""


# --------------------------------------------------------------------------
# derived pages
# --------------------------------------------------------------------------


def build_index(data: dict) -> str:
    stages = {s["n"]: s for s in data["stages"]}
    total_hours = sum(s["hours"] for s in data["stages"])
    done = sum(1 for s in data["stages"] if s["status"] == "done")

    cards = []
    for part in data["parts"]:
        part_stages = [stages[n] for n in part["stages"]]
        hours = sum(s["hours"] for s in part_stages)
        names = " · ".join(s["titleKo"] for s in part_stages)
        cards.append(
            f"""      <a class="card" href="parts/{part['slug']}/index.html">
        <span class="card-icon">{part['icon']}</span>
        <h3>{esc(part['title'])}</h3>
        <p>{esc(part['summary'])}</p>
        <span class="card-foot"><span>{esc(names)}</span><span>~{hours}h</span></span>
      </a>"""
        )

    rows = []
    for s in data["stages"]:
        rows.append(
            f"""        <a class="stage-row" href="stages/{stage_dir(s)}/index.html">
          <span class="stage-num">Stage {s['n']:02d}</span>
          <span class="stage-body">
            <strong>{esc(s['title'])}</strong>
            <span>{esc(s['summary'])}</span>
          </span>
          {status_badge(s)}
        </a>"""
        )

    body = f"""    <section class="hero">
      <p class="eyebrow">Curriculum · 14 stages</p>
      <h1>맨 땅에서 시작하는<br>DevOps 학습 경로</h1>
      <p class="lead">리눅스 셸 프롬프트에서 출발해 컨테이너, 파이프라인, 클라우드, 관측까지.
      각 단계는 읽고 끝나는 글이 아니라 직접 손을 움직여 확인하는 실습으로 구성됩니다.</p>
      <div class="hero-meta">
        <span>총 <b>{len(data['stages'])}</b>단계</span>
        <span><b>{len(data['parts'])}</b>개 파트</span>
        <span>예상 <b>{total_hours}</b>시간</span>
        <span>공개된 단계 <b>{done}</b>개</span>
      </div>
    </section>

    <h2 id="parts">파트별로 보기</h2>
    <p class="muted">14단계를 성격에 따라 다섯 파트로 묶었습니다. 각 파트 안에서는 순서대로 진행하는 것을 권장합니다.</p>
    <div class="grid cols-2">
{chr(10).join(cards)}
    </div>

    <h2 id="stages">전체 단계</h2>
    <div class="stage-list">
{chr(10).join(rows)}
    </div>

    <h2 id="how">이 사이트를 쓰는 법</h2>
    <div class="grid cols-3">
      <div class="card">
        <h3>1. 읽는다</h3>
        <p>각 단계는 개념 설명 → 명령어/코드 → 자주 하는 실수 순서로 이어집니다.</p>
      </div>
      <div class="card">
        <h3>2. 따라 친다</h3>
        <p>모든 예제는 복사해서 바로 실행할 수 있는 형태입니다. 눈으로 읽지 말고 쳐보세요.</p>
      </div>
      <div class="card">
        <h3>3. 체크한다</h3>
        <p>단계 하단의 체크리스트는 브라우저에 저장됩니다. 끝낸 항목을 표시하며 진행하세요.</p>
      </div>
    </div>
"""
    return shell(
        "DevOps Learning Path — 14단계 학습 경로",
        "리눅스부터 보안까지, 14단계로 구성된 DevOps 학습 커리큘럼.",
        0,
        body,
    )


def build_part(data: dict, part: dict) -> str:
    stages = {s["n"]: s for s in data["stages"]}
    part_stages = [stages[n] for n in part["stages"]]
    hours = sum(s["hours"] for s in part_stages)
    order = [p["slug"] for p in data["parts"]]
    idx = order.index(part["slug"])

    rows = []
    for s in part_stages:
        rows.append(
            f"""      <a class="stage-row" href="../../stages/{stage_dir(s)}/index.html">
        <span class="stage-num">Stage {s['n']:02d}</span>
        <span class="stage-body">
          <strong>{esc(s['title'])}</strong>
          <span>{esc(s['summary'])}</span>
        </span>
        <span class="badge">~{s['hours']}h</span>
        {status_badge(s)}
      </a>"""
        )

    prev_link = (
        f'<a href="../{data["parts"][idx - 1]["slug"]}/index.html">← {esc(data["parts"][idx - 1]["title"])}</a>'
        if idx > 0
        else '<a href="../../index.html">← 메인</a>'
    )
    next_link = (
        f'<a href="../{data["parts"][idx + 1]["slug"]}/index.html">{esc(data["parts"][idx + 1]["title"])} →</a>'
        if idx < len(data["parts"]) - 1
        else ""
    )

    body = f"""    <p class="crumbs"><a href="../../index.html">메인</a><span>/</span>{esc(part['title'])}</p>
    <section class="hero">
      <p class="eyebrow">{esc(part['subtitle'])}</p>
      <h1>{part['icon']} {esc(part['title'])}</h1>
      <p class="lead">{esc(part['summary'])}</p>
      <div class="hero-meta">
        <span><b>{len(part_stages)}</b>개 단계</span>
        <span>예상 <b>{hours}</b>시간</span>
      </div>
    </section>

    <h2>이 파트의 단계</h2>
    <div class="stage-list">
{chr(10).join(rows)}
    </div>

    <div class="pager">
      {prev_link}
      <span class="spacer"></span>
      {next_link}
    </div>
"""
    return shell(
        f"{part['title']} — DevOps Learning Path",
        part["summary"],
        2,
        body,
    )


def build_stage_stub(data: dict, stage: dict) -> str:
    parts = {p["slug"]: p for p in data["parts"]}
    part = parts[stage["part"]]
    ordered = sorted(data["stages"], key=lambda s: s["n"])
    idx = [s["n"] for s in ordered].index(stage["n"])
    prev_s = ordered[idx - 1] if idx > 0 else None
    next_s = ordered[idx + 1] if idx < len(ordered) - 1 else None

    prev_link = (
        f'<a href="../{stage_dir(prev_s)}/index.html">← Stage {prev_s["n"]:02d} {esc(prev_s["title"])}</a>'
        if prev_s
        else '<a href="../../index.html">← 메인</a>'
    )
    next_link = (
        f'<a href="../{stage_dir(next_s)}/index.html">Stage {next_s["n"]:02d} {esc(next_s["title"])} →</a>'
        if next_s
        else ""
    )

    body = f"""    <p class="crumbs"><a href="../../index.html">메인</a><span>/</span><a href="../../parts/{part['slug']}/index.html">{esc(part['title'])}</a><span>/</span>Stage {stage['n']:02d}</p>
    <section class="hero">
      <p class="eyebrow">Stage {stage['n']:02d} · {esc(part['subtitle'])}</p>
      <h1>{esc(stage['title'])}</h1>
      <p class="lead">{esc(stage['summary'])}</p>
      <div class="hero-meta">
        <span>예상 <b>{stage['hours']}</b>시간</span>
        <span>{status_badge(stage)}</span>
      </div>
    </section>

    <div class="placeholder">
      <h2>아직 작성 중입니다</h2>
      <p>이 단계의 본문은 준비 중입니다. 학습 계획에 따라 순서대로 채워집니다.</p>
      <p><a href="../../plan.html">전체 학습 계획 보기 →</a></p>
    </div>

    <div class="pager">
      {prev_link}
      <span class="spacer"></span>
      {next_link}
    </div>
"""
    return shell(
        f"Stage {stage['n']:02d}. {stage['title']} — DevOps Learning Path",
        stage["summary"],
        2,
        body,
    )


# --------------------------------------------------------------------------


def write(path: pathlib.Path, content: str, check: bool, changed: list) -> None:
    existing = path.read_text(encoding="utf-8") if path.exists() else None
    if existing == content:
        return
    changed.append(str(path.relative_to(ROOT)))
    if check:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--force",
        action="store_true",
        help="overwrite authored stage pages back to stubs — requires --stage",
    )
    ap.add_argument(
        "--stage",
        type=int,
        metavar="N",
        help="limit stage handling to this stage number",
    )
    ap.add_argument("--check", action="store_true", help="report staleness without writing")
    args = ap.parse_args()

    if args.force and args.stage is None:
        ap.error(
            "--force discards hand-written stage content, so it must name one stage: "
            "--force --stage N"
        )

    data = json.loads(DATA.read_text(encoding="utf-8"))
    changed: list = []

    write(SITE / "index.html", build_index(data), args.check, changed)
    for part in data["parts"]:
        write(SITE / "parts" / part["slug"] / "index.html", build_part(data, part), args.check, changed)

    for stage in data["stages"]:
        if args.stage is not None and stage["n"] != args.stage:
            continue
        target = SITE / "stages" / stage_dir(stage) / "index.html"
        if target.exists() and not args.force:
            continue
        write(target, build_stage_stub(data, stage), args.check, changed)

    if args.check:
        if changed:
            print("stale generated pages:", *changed, sep="\n  ")
            print("\nrun: python3 tools/scaffold.py")
            return 1
        print("site is up to date with data/curriculum.json")
        return 0

    if changed:
        print("wrote:", *changed, sep="\n  ")
    else:
        print("nothing to do — site already matches data/curriculum.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
