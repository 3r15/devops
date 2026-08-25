# DevOps Learning Path

리눅스에서 시작해 보안까지 이어지는 14단계 DevOps 학습 사이트입니다.
빌드 도구 없이 정적 HTML/CSS/JS로 만들어졌고, GitHub Pages로 배포됩니다.

🔗 **https://3r15.github.io/devops/**

## 구성

| 파트 | 내용 | 단계 |
| --- | --- | --- |
| Part 1 — 기반 다지기 | Linux · Networking · Git/GitHub | 1–3 |
| Part 2 — 자동화의 언어 | Bash · Python | 4–5 |
| Part 3 — 서비스와 컨테이너 | Web Servers · Docker · Kubernetes | 6–8 |
| Part 4 — 배포와 인프라 | CI/CD · Terraform · Ansible · Cloud | 9–12 |
| Part 5 — 운영과 보안 | Monitoring/Logging · Security | 13–14 |

전체 계획은 [`docs/LEARNING_PLAN.md`](docs/LEARNING_PLAN.md), 집필 규격은
[`docs/CONTENT_GUIDE.md`](docs/CONTENT_GUIDE.md)에 있습니다.

## 저장소 구조

```
CLAUDE.md                Claude Code용 저장소 안내
data/curriculum.json     커리큘럼 단일 진실 공급원 (파트/단계/시간/상태)
site/                    배포되는 정적 사이트
  index.html             메인 — 파트 카드 + 전체 단계 목록   [생성됨]
  parts/<slug>/          파트 페이지                        [생성됨]
  stages/<nn>-<slug>/    단계 본문                          [직접 작성]
  assets/                공용 CSS/JS
tools/scaffold.py        curriculum.json → 메인/파트 페이지 생성, 단계 스텁 생성
tools/check_links.py     사이트 내부 링크 검사
docs/                    학습 계획 및 집필 가이드
.claude/                 집필 자동화 (스킬 / 서브에이전트 / 검증 훅)
```

`[생성됨]` 페이지는 매번 다시 만들어집니다. 직접 고치지 말고 `data/curriculum.json`을 고친 뒤
스캐폴더를 다시 실행하세요. 단계 본문은 한 번 생성된 뒤로는 사람이 소유합니다
(`--force` 없이는 덮어쓰지 않습니다).

## 로컬에서 보기

```bash
python3 -m http.server 8000 --directory site
# http://localhost:8000
```

## 커리큘럼을 바꿨다면

```bash
python3 tools/scaffold.py       # 메인/파트 페이지 재생성 + 새 단계 스텁 생성
python3 tools/check_links.py    # 내부 링크 검사
python3 tools/scaffold.py --check   # CI와 동일한 동기화 검사
```

두 검사는 PR과 `main` push마다 CI에서도 돌고, `main`에 올라간 `site/`는
`.github/workflows/pages.yml`이 GitHub Pages로 배포합니다.

## 집필 자동화

`.claude/`에 이 저장소 전용 설정이 들어 있습니다.

| 종류 | 이름 | 하는 일 |
| --- | --- | --- |
| 스킬 | `/new-stage` | 단계 하나를 스캐폴딩 → 집필 → 상태 갱신 → 검증 → PR까지의 절차 |
| 서브에이전트 | `stage-author` | 집필 가이드에 맞춰 단계 본문 한 개를 작성 |
| 서브에이전트 | `stage-reviewer` | 머지 전 기술적 정확성 검수 (명령어를 실제로 검증) |
| 훅 | `PostToolUse` | `site/`·`data/`·`tools/`를 건드린 편집 직후 CI와 같은 두 검사를 자동 실행 |

훅은 검사가 실패하면 편집을 되돌리지 않고 실패 내용을 즉시 알려, 깨진 링크나 데이터와
어긋난 생성 페이지가 커밋에 섞이는 것을 막습니다.
