# 단계 페이지 집필 가이드

단계 본문(`site/stages/<nn>-<slug>/index.html`)을 쓸 때의 규칙입니다.
학습 계획은 [`LEARNING_PLAN.md`](LEARNING_PLAN.md)에 있습니다.

## 0. 시작하기 전에

```bash
python3 tools/scaffold.py     # 단계 스텁이 없으면 만들어 줍니다
```

스텁에는 헤더/푸터/브레드크럼/페이저가 이미 들어 있습니다. `<main>` 안의
`.placeholder` 블록만 본문으로 갈아끼우면 됩니다. **헤더·푸터·페이저의 경로는 손대지 마세요.**
생성기가 계산한 상대 경로이고, `tools/check_links.py`가 검사합니다.

## 1. 페이지 골격

절 순서는 고정입니다. 학습자가 열 번째 페이지에서도 원하는 곳을 바로 찾게 하기 위한 것입니다.

| 순서 | 절 | id | 필수 |
| --- | --- | --- | --- |
| 1 | 히어로 (제목/요약/시간/상태) | — | ✅ |
| 2 | 이 단계를 끝내면 | `goals` | ✅ |
| 3 | 준비물 | `prereq` | ✅ |
| 4 | 목차 | — | ✅ |
| 5 | 본문 절 5–9개 | 자유 | ✅ |
| 6 | 자주 하는 실수 | `pitfalls` | ✅ |
| 7 | 직접 해보기 | `exercises` | ✅ |
| 8 | 체크리스트 | `checklist` | ✅ |
| 9 | 더 읽을거리 | `further` | ✅ |
| 10 | 페이저 | — | ✅ (스텁에 포함) |

## 2. 문체

- **평서체(–다)**로 씁니다. "~해요"나 "~합시다"는 쓰지 않습니다.
- 한 문단은 4문장 이하. 명령어 사이의 설명은 두 문장이면 충분한 경우가 대부분입니다.
- 기술 용어는 영어를 그대로 둡니다(프로세스, 데몬, 마운트). 억지 번역 금지.
- 처음 나오는 약어는 한 번만 풀어 씁니다: "PID(process ID)".
- 겁주지 않습니다. 대신 위험한 명령에는 `.callout.warn`으로 무엇이 날아가는지 정확히 적습니다.

## 3. 명령어와 코드

- 모든 예제는 **복사해서 그대로 실행 가능**해야 합니다. 가상의 경로·호스트명을 쓸 때는
  치환할 자리임이 드러나게 `<user>`, `example.com`처럼 씁니다.
- 프롬프트 기호(`$`, `#`)는 붙이지 않습니다. 복사할 때 걸립니다.
- 출력이 이해에 필요하면 같은 블록에 `#` 주석으로 붙입니다.

```html
<pre><code>ls -l /var/log
# -rw-r----- 1 syslog adm 41K Aug 25 09:12 syslog</code></pre>
```

- `sudo`는 정말 필요할 때만 붙입니다. 붙였다면 왜 필요한지 한 줄 설명합니다.
- HTML 안에서 `<`, `>`, `&`는 반드시 `&lt;`, `&gt;`, `&amp;`로 이스케이프합니다.
  파이프와 리다이렉션 예제에서 가장 자주 깨집니다.

## 4. 재사용 가능한 컴포넌트

`site/assets/css/main.css`에 이미 있는 것들입니다. 새 클래스를 만들기 전에 여기부터 봅니다.

```html
<!-- 강조 박스: 기본 / 경고 / 확인 -->
<div class="callout">
  <p class="callout-title">💡 알아두기</p>
  <p>본문</p>
</div>
<div class="callout warn"> … </div>
<div class="callout ok"> … </div>

<!-- 목차 -->
<nav class="toc">
  <p>목차</p>
  <ol><li><a href="#section-id">절 제목</a></li></ol>
</nav>

<!-- 가로로 넘칠 수 있는 표는 반드시 감쌉니다 -->
<div class="table-scroll"><table> … </table></div>

<!-- 진행률이 저장되는 체크리스트 -->
<div class="progress-bar" data-progress-for="stage-01"><i></i></div>
<span data-progress-label></span>
<ul class="checklist" data-progress="stage-01">
  <li>
    <input type="checkbox" id="s01-c1">
    <label for="s01-c1">완료 기준 문장</label>
  </li>
</ul>
```

체크리스트 규칙:
- `data-progress` 값은 단계마다 유일해야 합니다 (`stage-01`, `stage-02`, …).
  이 값이 `localStorage` 키가 되므로 **한 번 정하면 바꾸지 않습니다.** 바꾸면 학습자의 진행률이 사라집니다.
- 각 `<input>`의 `id`도 유일해야 하고(`s01-c1`), 같은 이유로 재사용 중에는 바꾸지 않습니다.
- 항목은 "배웠다"가 아니라 **확인 가능한 행동**으로 씁니다.
  나쁨: "권한을 이해했다" / 좋음: "`chmod 640`을 적용한 파일을 다른 사용자로 읽으려 하면
  거부되는 것을 직접 확인했다"

## 5. "자주 하는 실수" 쓰는 법

에러 메시지를 **먼저** 보여주고 원인을 답합니다. 검색해서 이 페이지에 도착하는 사람은
개념이 아니라 그 메시지를 들고 옵니다.

```html
<h3>Permission denied (publickey)</h3>
<pre><code>ssh user@host
# user@host: Permission denied (publickey).</code></pre>
<p>서버가 비밀번호 인증을 끄고 공개키만 받는 상태다. …</p>
```

## 6. 링크

- 내부 링크는 상대 경로만 씁니다. 절대 경로(`/stages/...`)는 프로젝트 페이지
  (`/devops/` 하위 배포)에서 깨집니다.
- 외부 링크는 공식 문서를 우선합니다. 블로그 글은 대체 불가능할 때만.
- 앵커(`#id`)도 검사 대상입니다. 존재하지 않는 id를 가리키면 CI가 막습니다.

## 7. 마무리 체크

```bash
python3 tools/scaffold.py --check    # 파생 페이지가 데이터와 일치하는가
python3 tools/check_links.py         # 링크와 앵커가 다 살아 있는가
python3 tools/check_structure.py     # 태그 균형과 진행률 키 충돌
python3 -m http.server 8000 --directory site   # 눈으로 확인
```

그리고 `data/curriculum.json`에서 해당 단계의 `status`를 `done`으로 바꾸고
`python3 tools/scaffold.py`를 다시 돌립니다. 이걸 빼먹으면 메인 페이지 배지가 거짓말을 합니다.
