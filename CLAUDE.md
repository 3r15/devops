# CLAUDE.md

DevOps 학습 사이트 저장소. 정적 HTML/CSS/JS + GitHub Pages, 빌드 도구 없음.

## 먼저 읽을 것

- `docs/LEARNING_PLAN.md` — 14단계 학습/집필 계획, 관통 예제, 릴리스 순서
- `docs/CONTENT_GUIDE.md` — 단계 페이지 집필 규격 (골격, 문체, 컴포넌트)

## 핵심 규칙

`data/curriculum.json`이 커리큘럼의 단일 진실 공급원이다. 파트·단계·예상 시간·공개 상태가
모두 여기서 나온다.

페이지는 두 종류다.

- **생성 페이지** — `site/index.html`, `site/parts/**`. `tools/scaffold.py`가 만든다.
  **직접 수정하지 않는다.** 고치려면 `data/curriculum.json`을 고치고 생성기를 다시 돌린다.
- **집필 페이지** — `site/stages/**`, `site/plan.html`, `site/about.html`. 사람이 소유한다.
  생성기는 한 번 만들어진 뒤로는 덮어쓰지 않는다. 스텁으로 되돌리려면
  `--force --stage N`으로 단계를 지정해야 한다 — 인자 없는 `--force`는 거부된다.

단계를 새로 쓰거나 마무리할 때는 `/new-stage` 스킬을 쓴다.

## 검증

```bash
python3 tools/scaffold.py --check    # 생성 페이지가 데이터와 일치하는가
python3 tools/check_links.py         # 내부 링크/앵커가 살아 있는가
```

두 명령은 CI(`.github/workflows/ci.yml`)와 배포(`pages.yml`)에서도 돌고,
`.claude/hooks/verify-site.py`가 `site/`·`data/`·`tools/`를 건드린 편집 직후에도 돌린다.
훅이 exit 2로 막으면 그 자리에서 고친다. 검사를 우회하지 않는다.

## 서브에이전트

- `stage-author` — 단계 본문 한 개를 규격에 맞춰 집필
- `stage-reviewer` — 머지 전 기술적 정확성 검수 (명령어를 실제로 검증)

## 절대 하지 말 것

- 공개된 단계의 `data-progress` 키나 체크박스 `id` 변경 — `localStorage`에 저장된
  학습자 진행률이 사라진다.
- 사이트 내부 링크에 절대 경로(`/stages/...`) 사용 — `/devops/` 하위로 배포되므로 깨진다.
- 한 PR에 여러 단계 담기.
