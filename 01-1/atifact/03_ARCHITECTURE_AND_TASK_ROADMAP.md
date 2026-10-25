# B1-1 전체 아키텍처 및 작업 로드맵 (ARCHITECTURE_AND_TASK_ROADMAP)

본 문서는 B1-1 반응형 포트폴리오 웹사이트의 전체 시스템 구조, 상태 머신 전이 흐름, 데이터 변환 파이프라인 및 Phase별 세부 실행 로드맵을 종합적으로 정의합니다.

---

## 1. 엔드투엔드 런타임 아키텍처 (End-to-End Architecture)

브라우저가 `index.html`을 로드한 시점부터 각 컴포넌트가 활성화되는 전체 런타임 생명주기를 시각화한 구조도입니다.

```
+---------------------------------------------------------------------------------------+
|                                    BROWSER RUNTIME                                    |
+---------------------------------------------------------------------------------------+
       │
       │ 1. GET /index.html (HTML Parsing & DOM Tree Construction)
       ▼
+───────────────────────────────────────────────────────────────────────────────────────+
|                                      index.html                                       |
|  - <head>: Google Fonts (Inter), Font Awesome Icons, style.css                        |
|  - <header>: Navigation Bar (Logo, Nav Links, Dark Theme Toggle, Hamburger Button)    |
|  - <main>: Hero, About, Skills, Projects (API Section), Contact (Form Section)        |
|  - <footer>: Copyright, Social Profiles Link                                          |
|  - <script type="module" src="js/main.js">                                            |
+───────────────────────────────────────────────────────────────────────────────────────+
       │
       │ 2. ES Module Execution (Deferred & Scoped)
       ▼
+───────────────────────────────────────────────────────────────────────────────────────+
|                                      js/main.js                                       |
|  [Orchestrator & Global State Bootstrap]                                              |
|   ├─ initTheme(): LocalStorage 확인 후 <html> data-theme 속성 동기화                    |
|   ├─ initNavigation(): 햄버거 메뉴 토글 및 스무스 스크롤 바인딩                            |
|   ├─ initScrollObserver(): IntersectionObserver로 섹션 등장 페이드인 등록                 |
|   ├─ initScrollToTop(): 스크롤 300px 감지 플로팅 버튼 제어                              |
|   └─ initProjects(): api.js 호출 및 로딩 파이프라인 트리거                                |
+───────────────────────┬───────────────────────────────────────┬───────────────────────+
                        │                                       │
            (비동기 데이터 요청)                      (이벤트 바인딩)
                        ▼                                       ▼
+───────────────────────────────────────+       +───────────────────────────────────────+
|               js/api.js               |       |             js/events.js              |
|  [GitHub REST API Client]             |       |  [Form Validation & Interaction]      |
|   - Endpoint: /users/{user}/repos     |       |   - 실시간 Regex 이메일 유효성 검사   |
|   - 4대 상태 머신 제어                |       |   - 빈 필드 감지 및 에러 메시지 바인딩|
|   - Rate Limit (403) 및 통신 오류 포착|       |   - event.preventDefault() 캡슐화     |
+───────────────────┬───────────────────+       +───────────────────┬───────────────────+
                    │                                               │
                    │ (데이터 가공)                                 │ (검증 완료 알림)
                    ▼                                               ▼
+───────────────────────────────────────────────────────────────────────────────────────+
|                                       js/ui.js                                        |
|  [DOM Mutation & View Layer]                                                          |
|   ├─ renderLoading(): Projects 영역에 SVG 스피너 렌더링                               |
|   ├─ renderCards(repos): 고차함수 map()과 escapeHTML()로 카드 DOM 동적 삽입          |
|   ├─ renderError(message, retryCb): 에러 안내문 및 재시도 버튼 이벤트 연결             |
|   ├─ renderEmpty(): 빈 상태 안내 일러스트/메시지 렌더링                               |
|   └─ renderFormFeedback(field, isValid, msg): 폼 에러/성공 토스트 렌더링              |
+───────────────────────────────────────────────────────────────────────────────────────+
```

---

## 2. GitHub API 4대 상태 머신 전이 다이어그램 (State Machine)

Projects 섹션은 정적 HTML이 아니며, 외부 통신 결과에 따라 아래 **5개 상태(상태 머신)** 중 정확히 하나를 가집니다.

```
                  ┌────────────────────────┐
                  │      STATE: IDLE       │
                  │ (초기화 직전 대기 상태) │
                  └───────────┬────────────┘
                              │
                    [Projects 로드 이벤트 트리거]
                              │
                              ▼
                  ┌────────────────────────┐
                  │     STATE: LOADING     │ ──▶ ui.renderLoading()
                  │ (네트워크 요청 전송 중) │     (애니메이션 스피너 노출)
                  └───────────┬────────────┘
                              │
                   [fetch() Promise Settlement]
                              │
            ┌─────────────────┴─────────────────┐
            │                                   │
      [HTTP 200 OK]                    [Network Fail or 403]
            │                                   │
            ▼                                   ▼
    [repos.length > 0 ?]                ┌────────────────────────┐
            │                           │      STATE: ERROR      │ ──▶ ui.renderError()
     ┌──────┴──────┐                    │ (403 한도초과/네트워크)|     (에러문 + 재시도 버튼)
    YES            NO                   └───────────┬────────────┘
     │              │                               │
     ▼              ▼                        [재시도 버튼 클릭]
┌─────────┐   ┌─────────┐                           │
│ STATE:  │   │ STATE:  │                           │
│ SUCCESS │   │  EMPTY  │                           └─────────────────────┐
└────┬────┘   └────┬────┘                                                 │
     │             │                                                      │
     │             └───────────▶ ui.renderEmpty()                         │
     │                           ("등록된 프로젝트가 없습니다" UI)         │
     │                                                                    │
     └─────────────────────────▶ ui.renderCards()                         │
                                 (정렬된 카드 그리드 렌더링)               │
                                                                          ▼
                                                             [다시 LOADING 상태로 진입]
```

---

## 3. 데이터 변환 파이프라인 (Data Transformation Pipeline)

GitHub API의 방대한 Raw JSON 데이터를 브라우저 뷰(Card DOM)로 변환하는 정제 매트릭스입니다.

| 단계 | 데이터 주체 | 형태 및 구조 | 변환 처리 모듈 |
| :---: | :--- | :--- | :--- |
| **Step 1** | **Raw API Data** | 수십 개 필드를 가진 원시 JSON 배열 (`id`, `node_id`, `owner`, `permissions`, ...) | `api.js` (GitHub REST API) |
| **Step 2** | **Sanitized Data** | Fork된 저장소 제외(`fork === false`), 최근 업데이트순 정렬, 상위 6개 추출 | `api.js` (`filter()`, `slice()`) |
| **Step 3** | **Card ViewModel** | `{ name, desc, lang, stars, forks, url }` 필수 6개 키로 축약된 순수 객체 | `ui.js` (`map()` 변환) |
| **Step 4** | **Escaped String** | 특수문자(`<`, `>`, `&`, `"`)를 HTML 엔티티로 치환하여 XSS 방어 처리 | `ui.js` (`escapeHTML()`) |
| **Step 5** | **DOM Tree** | `<article class="project-card">` HTML 요소로 조립되어 `.projects-grid`에 마운트 | `ui.js` (`innerHTML` or `appendChild`) |

---

## 4. Contact 폼 유효성 검사 생명주기 (Form Lifecycle)

```
[사용자 입력 필드 타이핑 (input 이벤트)]
                   │
                   ▼
       [실시간 밸리데이션 검사]
       ├─ 이름: trim().length >= 2
       ├─ 이메일: /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)
       └─ 메시지: trim().length >= 10
                   │
       ┌───────────┴───────────┐
      [유효]                  [무효]
       │                       │
       ▼                       ▼
 ui.clearFieldError()    ui.renderFieldError()
 (테두리 정상화)         (붉은 테두리 + 경고 텍스트 표시)
                   │
[사용자 최종 제출 버튼 클릭 (submit 이벤트)]
                   │
                   ▼
       [event.preventDefault()] ── 브라우저 새로고침 차단
                   │
       [모든 필드 최종 종합 검증]
                   │
       ┌───────────┴───────────┐
     [통과]                  [실패]
       │                       │
       ▼                       ▼
 ui.renderSubmitSuccess() ui.focusFirstInvalidField()
 (성공 안내 메시지 출력)  (첫 번째 에러 인풋으로 포커스 이동)
 폼 인풋 초기화 (reset)
```

---

## 5. 다크 모드 테마 전파 및 영속화 흐름도

```
[페이지 로드 시점]
       │
       ▼
[localStorage.getItem('theme') 검사]
       ├─ 값이 존재함 ('dark' or 'light') ──▶ 해당 테마 적용
       └─ 값 없음 (최초 방문자) ────────────▶ prefers-color-scheme 시스템 설정 감지
       │
       ▼
document.documentElement.dataset.theme = 'dark' | 'light'
       │
       ▼
[CSS 엔진이 변수 자동 치환]
  --color-bg, --color-surface, --color-text 등 즉시 전환

─────────────────────────────────────────────────────────────────────────────

[사용자가 #theme-toggle 버튼 클릭]
       │
       ▼
현재 dataset.theme 확인 ('dark' ↔ 'light' 스왑)
       │
       ├─ document.documentElement.dataset.theme 변경 (즉각 화면 반응)
       ├─ localStorage.setItem('theme', newTheme) (브라우저 영속화)
       └─ 토글 버튼 내 아이콘 전환 (달 아이콘 ↔ 해 아이콘)
```

---

## 6. Phase별 실행 로드맵 및 산출물 매트릭스

| Phase | 단계 명칭 | 핵심 목표 | 산출물 파일 | 검증 게이트 (Exit Gate) |
| :---: | :--- | :--- | :--- | :--- |
| **Phase 1** | 과제 분석 | 요구사항 전수 명세화 | `TASK_SPECIFICATION.md`, `promise_ledger.md` | 32개 약속 목록 도출 완료 |
| **Phase 2** | 사전 설계 선행 | 6대 엔지니어링 아티팩트 완비 | `atifact/01~06.md` 6종 | 6종 동시 완성 및 콘텐츠 기준 충족 |
| **Phase 3A** | 환경 구성 | 형상 관리 및 보안 파일 설정 | `.gitignore` | 민감/임시 파일 차단 설정 확인 |
| **Phase 3B** | 코드 구현 | 바닐라 웹 모듈 완성 | `index.html`, `style.css`, `js/*.js` (4종) | HTML 유효성 및 JS 모듈 에러 0건 |
| **Phase 4** | 브라우저 실증 | 전 기능 브라우저 통합 검증 | 브라우저 렌더링 및 인터랙션 실증 | 6대 인터랙션 및 4대 API 상태 정상 |
| **Phase 5** | 테스트 가이드 | 평가자용 단계별 실행서 작성 | `STEP_BY_STEP_EXECUTION_AND_TEST_GUIDE.md` | 5단계 기술 규격 완비 |
| **Phase 6** | 평가 대시보드 | 인터랙티브 기술 평가 도구 구축 | `web_evaluation/index.html` | 브라우저 무결성 대시보드 렌더링 |
| **Phase 7** | 배포 및 검증 | 정적 호스팅 라이브 릴리즈 | GitHub Pages 배포 URL | 외부 네트워크 정상 접속 확인 |
| **Phase 8** | 완료 선언 | 최종 품질 감사 및 종료 | `promise_ledger.md` (100% 달성) | 32개 체크박스 전수 체크 |
