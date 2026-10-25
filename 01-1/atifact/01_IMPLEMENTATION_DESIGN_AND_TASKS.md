# B1-1 반응형 포트폴리오 웹사이트 상세 구현 설계서 및 작업 태스크 (IMPLEMENTATION_DESIGN_AND_TASKS)

---

## 1. 과제 요구사항 100% 전수 점검 및 검증 매트릭스

| 번호 | 요구 기능 및 제약 조건 | 세부 규칙 및 기대 동작 | 설계 반영 모듈 |
| :---: | :--- | :--- | :--- |
| **R-01** | **순수 바닐라 웹 기술 한정** | React, Vue, jQuery, Bootstrap, Tailwind CSS 등 외부 라이브러리 사용 0건 | 전체 프로젝트 |
| **R-02** | **허용 외부 리소스 규격** | Google Fonts(웹폰트), Font Awesome(아이콘 CDN)만 link 태그로 허용 | `index.html` |
| **R-03** | **시맨틱 마크업 준수** | `header`, `nav`, `main`, `section`, `article`, `footer` 태그를 적재적소에 배치 | `index.html` |
| **R-04** | **6대 필수 섹션 구성** | Hero, About, Skills, Projects, Contact, Footer 6개 섹션 완비 | `index.html` |
| **R-05** | **네비게이션 앵커 링크** | 로고(왼쪽), 메뉴(오른쪽), 각 섹션 ID로 부드럽게 이동하는 앵커 구현 | `index.html`, `main.js` |
| **R-06** | **모바일 햄버거 메뉴** | 768px 미만에서 메뉴 숨김 처리 및 햄버거 버튼 토글 인터랙션 구현 | `style.css`, `main.js` |
| **R-07** | **다크 모드 테마 스위처** | CSS Variables 기반 라이트/다크 테마 전환 및 `localStorage` 영속화 | `style.css`, `main.js` |
| **R-08** | **모바일 퍼스트 반응형 레이아웃** | 브레이크포인트(768px 태블릿, 1024px 데스크톱) 기준 미디어 쿼리 구축 | `style.css` |
| **R-09** | **CSS 레이아웃 분할 전략** | Nav바는 Flexbox, Projects 카드 및 Skills 배지는 CSS Grid 적용 | `style.css` |
| **R-10** | **스크롤 이벤트 인터랙션** | 스크롤 60px 이상 시 헤더 스타일 변경, 300px 이상 시 Scroll-to-Top 버튼 노출 | `main.js` |
| **R-11** | **스크롤 등장 애니메이션** | `IntersectionObserver` API(threshold 0.2) 기반 뷰포트 진입 fade-in | `style.css`, `main.js` |
| **R-12** | **GitHub Repos API 비동기 연동** | `fetch` + `async/await`로 사용자 공개 저장소 6개 동적 수집 | `api.js` |
| **R-13** | **API 4대 상태 UI 표현** | 로딩(스피너), 성공(카드 그리드), 실패(에러 메시지+재시도), 빈 상태(안내문) | `ui.js`, `api.js` |
| **R-14** | **카드 데이터 렌더링 규격** | 저장소 이름, 설명, 주 언어, Star 수, Fork 수, GitHub 링크 포함 | `ui.js` |
| **R-15** | **Contact 폼 유효성 검사** | 이름/이메일/메시지 빈값 방지, 이메일 정규식 검증, 실시간 에러 출력 | `events.js` |
| **R-16** | **폼 전송 이벤트 캡슐화** | `event.preventDefault()` 기본 동작 차단 후 성공 피드백 메시지 렌더링 | `events.js` |
| **R-17** | **모던 ES6+ 문법 준수** | `var` 사용 0건, `const`/`let`, 화살표 함수, 템플릿 리터럴, 구조분해 할당 | 전체 JS 파일 |
| **R-18** | **배열 고차 함수 활용** | `map`, `filter`, `forEach`를 활용한 선언적 데이터 변환 및 렌더링 | `ui.js`, `api.js` |
| **R-19** | **웹 접근성(a11y) 보장** | 폼 `label for="id"` 100% 매핑, 모든 이미지 의미 있는 `alt` 속성 부여 | `index.html`, `ui.js` |
| **R-20** | **배포 및 무결성 검증** | GitHub Pages 정적 호스팅 배포 및 브라우저 콘솔 에러 0건 보장 | GitHub 배포 |

---

## 2. 컴팩트 모듈 아키텍처 및 책임 분리 (SRP Architecture)

```
/Users/hwangjeonghyeon/codyssey_2026/2-1/B1-1/
├── index.html           # [구조 계층] 6대 섹션 시맨틱 마크업, SEO 메타데이터, 폰트 로드
├── css/
│   └── style.css        # [표현 계층] CSS Variables, 다크모드, 반응형 미디어쿼리, 애니메이션
├── js/
│   ├── main.js          # [조율 계층] 전체 초기화, 테마 관리, 스크롤 감지, 네비게이션 제어
│   ├── api.js           # [통신 계층] GitHub REST API 비동기 요청, 4대 상태 전이 관리
│   ├── ui.js            # [렌더링 계층] 순수 DOM 조작, 카드 템플릿 매핑, 상태별 UI 업데이트
│   └── events.js        # [인터랙션 계층] 폼 유효성 정규식 검사, 이벤트 리스너 바인딩
├── images/              # [자산 계층] 프로필 사진, 파비콘, 프로젝트 썸네일 등 정적 이미지
├── atifact/             # [설계 계층] 사전 엔지니어링 설계 및 학습 아티팩트 6종
├── web_evaluation/      # [평가 계층] 브라우저 기반 기술 평가 대시보드
├── TASK_SPECIFICATION.md# [명세 계층] 과제 기능 및 제약조건 전수 명세
├── STEP_BY_STEP_EXECUTION_AND_TEST_GUIDE.md # [실행 계층] 챕터별 검증 및 테스트 가이드
└── README.md            # [공개 계층] 프로젝트 개요, 배포 URL, 스크린샷 가이드
```

### 계층별 의존성 흐름도 (Unidirectional Dependency)
```
         ┌───────────────────┐
         │    index.html     │
         └─────────┬─────────┘
                   │ <script type="module" src="js/main.js">
                   ▼
         ┌───────────────────┐
         │      main.js      │ ── 전역 상태(테마, 스크롤) 초기화 및 오케스트레이션
         └─────┬───────┬─────┘
               │       │
       ┌───────┘       └───────┐
       ▼                       ▼
┌──────────────┐       ┌──────────────┐
│    api.js    │       │  events.js   │
└──────┬───────┘       └──────┬───────┘
       │                      │
       │ (데이터 전달)          │ (검증 후 UI 요청)
       ▼                      ▼
┌─────────────────────────────────────┐
│                ui.js                │ ── DOM 직접 조작 및 화면 렌더링 전담
└─────────────────────────────────────┘
```

---

## 3. 심층 엔지니어링 고려 사항 및 아키텍처적 추론 (Deep Engineering Rationale)

단순히 화면만 나오는 일회성 코드가 아닌, 실무 프론트엔드 엔지니어링의 원칙을 반영한 **5대 핵심 아키텍처 설계 의사결정**입니다.

### 1) 외부 프레임워크(React/Tailwind) 완전 배제 및 순수 Vanilla Web 채택
* **엔지니어링 추론**:
  * React나 Vue 같은 라이브러리는 브라우저의 기본 동작(DOM 렌더링, 이벤트 버블링, 비동기 큐)을 가상 DOM(Virtual DOM)과 합성 이벤트(SyntheticEvent) 뒤로 추상화하여 감춥니다.
  * 기초가 탄탄하지 않은 상태에서 프레임워크를 사용하면, 사소한 렌더링 이슈나 성능 병목 현상이 발생했을 때 브라우저 엔진의 렌더 트리 재구성(Reflow/Repaint) 단계를 이해하지 못해 해결할 수 없습니다.
  * 따라서 순수 HTML5 시맨틱 마크업, 순수 CSS3 Grid/Flexbox, ES6+ Modules 체계를 구축함으로써 브라우저 런타임의 본질을 100% 실증적으로 제어하도록 설계함.

### 2) "이벤트 → 상태 변경 → DOM 렌더링" 단방향 아키텍처 구축
* **엔지니어링 추론**:
  * 일반적인 초보자 코드는 이벤트 리스너 내부에서 직접 스타일을 바꾸고, 텍스트를 고치고, 통신을 수행하는 등 관심사 분리가 무너져 있습니다(Spaghetti Code).
  * 이를 방지하기 위해 React의 상태 관리 철학을 모방하여 **중앙 상태 객체(State Object)** 를 두고, 이벤트는 오직 상태만 변경하며, 화면은 상태 변화에 반응하여 렌더링 함수(`renderCards`, `renderTheme`)를 호출하는 단방향 데이터 흐름을 정립함.
  * 결과적으로 UI와 비즈니스 로직이 완전히 분리되어 코드 재사용성과 유지보수성이 극대화됨.

### 3) GitHub REST API 비동기 통신과 4대 상태 머신(State Machine) 설계
* **엔지니어링 추론**:
  * 네트워크 통신은 절대 "성공"만 존재하지 않습니다. 모바일 환경의 불안정한 연결, 서버 에러(500), 미인증 API 요청의 시간당 60회 제한(403 Rate Limit), 저장소가 0개인 신규 계정 등 다양한 상태가 존재함.
  * 단순한 `fetch().then()` 구조를 탈피하고, `apiState` 머신을 `idle`, `loading`, `success`, `error`, `empty`의 5단계로 정형화함.
  * 각 상태 전이에 따라 UI 모듈(`ui.js`)이 스피너 표시, 에러 안내문 + 재시도 버튼, 빈 화면 플레이스홀더를 전담 렌더링하도록 캡슐화함.

### 4) CSS Variables 기반의 무깜빡임(Zero-FOUC) 다크 모드 설계
* **엔지니어링 추론**:
  * JavaScript로 모든 요소의 인라인 스타일(`element.style.background`)을 직접 덮어씌우는 방식은 성능 낭비와 스타일 충돌을 유발함.
  * 최상위 `:root`와 `[data-theme="dark"]` 선택자에 CSS 변수를 선언하고, JS는 최상위 태그의 속성(`document.documentElement.dataset.theme`)만 변경하도록 설계함.
  * 페이지 로드 시 인라인 스크립트 또는 최초 동기 스크립트에서 `localStorage`의 테마 값을 즉시 읽어 `data-theme`를 선적용함으로써, 페이지 새로고침 시 화면이 하얗게 번쩍이는 FOUC(Flash of Unstyled Content) 현상을 원천 방어함.

### 5) innerHTML 보안 가드레일 및 XSS(Cross-Site Scripting) 방어
* **엔지니어링 추론**:
  * GitHub API로부터 받아온 데이터(`repo.name`, `repo.description`)를 아무런 검증 없이 `innerHTML`에 삽입할 경우, 저장소 설명에 악의적인 `<script>`나 `<img onerror="...">` 태그가 포함되어 있을 시 스크립트 인젝션 공격에 취약해짐.
  * 해결책:
    1. 사용자 입력이나 외부 API 수신 데이터를 삽입할 때는 `textContent` 속성을 우선 사용함.
    2. 동적 HTML 템플릿 리터럴 생성 시 HTML 특수문자(`&`, `<`, `>`, `"`, `'`)를 엔티티로 치환하는 `escapeHTML()` 새니타이저 함수를 `ui.js`에 내장하여 XSS 취약점을 100% 차단함.

---

## 4. 세부 작업 실행 태스크 목록 (Task Breakdown)

### PHASE 1 — 과제 분석 및 명세 확정 ✅
- [x] T-01: 요구사항 원문 분석 및 32개 필수 약속 원장(`promise_ledger.md`) 수립
- [x] T-02: `TASK_SPECIFICATION.md` 작성 및 금기 규칙/완료 기준 정의

### PHASE 2 — 사전 설계 문서 6종 완비 (현재 단계)
- [ ] T-03: `01_IMPLEMENTATION_DESIGN_AND_TASKS.md` 작성 (요구사항 매트릭스, SRP, 5대 설계 추론)
- [ ] T-04: `02_LEARNING_GUIDE_FOR_BEGINNERS.md` 작성 (비유→기술→코드 3단계 학습서, FAQ 5종)
- [ ] T-05: `03_ARCHITECTURE_AND_TASK_ROADMAP.md` 작성 (시스템 구조도, 4대 상태 흐름도, 로드맵)
- [ ] T-06: `04_ENGINEERING_DECISIONS_AND_TRADE_OFFS.md` 작성 (5대 기술선택 Why/트레이드오프, 가드레일)
- [ ] T-07: `05_COMPREHENSIVE_ALGORITHM_AND_CODE_DEEP_DIVE.md` 작성 (모듈별 5단계 구조적 알고리즘 분석)
- [ ] T-08: `06_EVALUATION_AND_EXECUTION_GUIDE.md` 작성 (기능 총람, 검증 시나리오, 자가 검증문)

### PHASE 3 — 환경 준비 및 소스코드 구현
- [ ] T-09: [3A] `.gitignore` 작성 (OS 임시파일, 에디터 설정, 로그 파일 차단)
- [ ] T-10: [3B-1] `index.html` 6대 섹션 시맨틱 마크업 구축 및 a11y 속성 부여
- [ ] T-11: [3B-2] `css/style.css` CSS Variables, Reset, 모바일 퍼스트 반응형 레이아웃 작성
- [ ] T-12: [3B-3] `js/api.js` GitHub REST API 통신 및 4대 상태 머신 구현
- [ ] T-13: [3B-4] `js/ui.js` 동적 카드 렌더링, XSS 새니타이징, 상태별 뷰 전환 로직 구현
- [ ] T-14: [3B-5] `js/events.js` 실시간 정규식 폼 유효성 검사 및 에러 피드백 구현
- [ ] T-15: [3B-6] `js/main.js` 전역 초기화, 테마 스위처, IntersectionObserver 스크롤 애니메이션 연동

### PHASE 4 — 브라우저 통합 실증 검증
- [ ] T-16: 로컬 웹서버 구동 및 데스크톱/모바일 뷰포트 렌더링 검증
- [ ] T-17: 6대 인터랙션 동작 실증 (다크모드, 햄버거, 스크롤 TOP, 폼 검증, API 4대 상태)
- [ ] T-18: 브라우저 콘솔 에러 0건 및 네트워크 탭 통신 실증 캡처

### PHASE 5 — 실행 및 테스트 매뉴얼 작성
- [ ] T-19: `STEP_BY_STEP_EXECUTION_AND_TEST_GUIDE.md` 작성 (5단계 규격 준수)

### PHASE 6 — 기술 평가 마스터 대시보드 구축
- [ ] T-20: `web_evaluation/index.html` 인터랙티브 기술 평가 대시보드 완성

### PHASE 7 — 배포 및 검증
- [ ] T-21: GitHub Pages 배포 설정 및 외부 라이브 URL 접속 검증

### PHASE 8 — 최종 완료 선언 및 약속 원장 동결
- [ ] T-22: `promise_ledger.md` 32개 항목 전수 100% 이행 확인 및 최종 보고
