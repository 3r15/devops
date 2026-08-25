---
name: new-stage
description: Add or complete one stage of the DevOps learning site — scaffold the page, write the body to the content guide, update curriculum status, verify, and open a PR. Use when asked to write, implement, or finish a stage (e.g. "Stage 3 작성해줘", "다음 단계 구현해줘", "Docker 단계 채워줘").
---

# 단계 하나 구현하기

한 단계 = 한 PR. 이 순서를 지키면 생성 페이지와 본문이 어긋나지 않는다.

## 1. 대상 확인

```bash
python3 -c "
import json
d = json.load(open('data/curriculum.json'))
for s in d['stages']:
    print(f\"{s['n']:02d} {s['status']:8} {s['slug']:14} {s['title']}\")
"
```

단계 번호가 지정되지 않았다면 `planned` 중 가장 번호가 작은 것이 다음 대상이다.
앞 단계가 아직 `planned`인데 뒤 단계를 먼저 쓰라는 요청이면, 예제가 어긋난다는 점을 한 줄로
알리고 요청대로 진행한다.

## 2. 브랜치와 상태

```bash
git checkout -b stage/<nn>-<slug>
```

`data/curriculum.json`에서 해당 단계 `status`를 `wip`으로 바꾸고:

```bash
python3 tools/scaffold.py     # 스텁 생성 + 메인/파트 배지 갱신
```

## 3. 본문 작성

`docs/CONTENT_GUIDE.md`가 규격이고 `docs/LEARNING_PLAN.md`가 그 단계의 목표·산출물·완료 기준이다.
둘 다 읽고 시작한다. `site/stages/<nn>-<slug>/index.html`의 `.placeholder` 블록만 본문으로 바꾼다.
헤더·푸터·페이저는 손대지 않는다.

분량이 크거나 다른 작업과 병행해야 하면 `stage-author` 서브에이전트에 맡긴다.
작성이 끝나면 `stage-reviewer`로 검수한다. 리뷰어의 blocker와 major는 머지 전에 해소한다.

## 4. 완료 처리

`status`를 `done`으로 바꾸고 다시 생성한다.

```bash
python3 tools/scaffold.py
python3 tools/scaffold.py --check
python3 tools/check_links.py
```

`docs/LEARNING_PLAN.md`의 릴리스 표에서 해당 항목 상태도 갱신한다.

## 5. 눈으로 확인

```bash
python3 -m http.server 8000 --directory site
```

메인에서 파트로, 파트에서 단계로 들어가지는지, 다크/라이트 양쪽에서 읽히는지,
체크박스를 눌렀다 새로고침해도 유지되는지 본다.

## 6. 커밋과 PR

```bash
git add -A
git commit -m "Add Stage <nn>: <Title>"
git push -u origin stage/<nn>-<slug>
```

PR 본문에는 다룬 절, 체크리스트 항목 수, 사람이 확인해줬으면 하는 기술적 주장을 적는다.
`main`에 머지되면 `.github/workflows/pages.yml`이 알아서 배포한다.

## 하지 말 것

- `site/index.html`이나 `site/parts/**`를 직접 수정하는 것 — 다음 생성에서 덮어써진다.
  바꾸려면 `data/curriculum.json`을 고친다.
- 이미 공개된 단계의 `data-progress` 키나 체크박스 `id`를 바꾸는 것 — 학습자 진행률이 사라진다.
- 한 PR에 여러 단계를 담는 것 — 리뷰가 불가능해진다.
