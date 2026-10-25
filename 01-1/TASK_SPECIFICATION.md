# B1-1 반응형 포트폴리오 웹사이트 과제 명세서 (TASK_SPECIFICATION)

---

## 1. 미션 개요 및 의도

### 목적
HTML, CSS, JavaScript는 모든 웹 개발의 기초이며, 브라우저가 이해하는 유일한 언어다. 이 과제에서는 **외부 라이브러리 없이 순수 HTML/CSS/JavaScript만**으로 반응형 포트폴리오 웹사이트를 처음부터 끝까지 완성한다.

### 핵심 학습 목표
단순히 화면을 그리는 것이 아니라, **"사용자 이벤트 → DOM 조작 → 화면 변화"** 가 연결되는 웹의 동작 원리를 결과물로 확인하는 것이 핵심이다.

### 왜 이 과제가 중요한가 (React 학습의 전제 조건)
React의 컴포넌트, 상태, 이벤트 개념은 모두 이 과제에서 다루는 DOM 조작과 이벤트 처리를 추상화한 것이다. 이 과제를 완전히 이해하지 않으면 React의 작동 원리를 이해할 수 없다.

### 학습자가 스스로 설명할 수 있어야 하는 5대 목표
1. HTML 시맨틱 태그를 왜 사용하는지, 어떤 기준으로 구조를 설계했는지
2. CSS Flexbox와 Grid의 차이, 그리고 언제 각각을 선택하는지
3. `querySelector`로 DOM을 선택하고 `addEventListener`로 이벤트를 연결하는 흐름
4. 화살표 함수, 구조분해 할당, 배열 메서드(map/filter)가 왜 필요하고 어떻게 사용하는지
5. `fetch`와 `async/await`로 비동기 데이터를 가져오고, 로딩/성공/실패 상태를 UI로 표현하는 방법

---

## 2. 필수 제약 사항 및 금기 규칙

| 구분 | 제약 규격 및 규칙 | 위반 시 영향 |
| :--- | :--- | :--- |
| **외부 라이브러리 금지** | React, Vue, jQuery, Bootstrap, Tailwind CSS 절대 사용 금지 | 과제 목적 무효화 |
| **허용 외부 리소스** | Font Awesome(아이콘 CDN), Google Fonts(웹폰트)만 허용 | — |
| **var 금지** | `const`, `let`만 사용. `var` 0건 | 코드 품질 감점 |
| **inline onclick 금지** | HTML 속성 `onclick` 사용 금지. `addEventListener`만 허용 | 아키텍처 위반 |
| **inline style 금지** | `style=""` 속성 사용 금지. CSS 클래스로만 스타일 제어 | 아키텍처 위반 |
| **시맨틱 태그 의무** | `div`만으로 레이아웃 구성 금지. `header/nav/main/section/article/footer` 사용 | 접근성/SEO 감점 |
| **폼 label 연결** | 모든 폼 요소에 `<label for="id">` 연결 필수 | 접근성 위반 |
| **이미지 alt 의무** | 모든 `<img>`에 의미 있는 `alt` 속성 필수 | 접근성 위반 |
| **JavaScript defer 로드** | `<script defer src="...">` 사용 필수 | DOM 로드 순서 오류 |
| **GitHub API Rate Limit** | 인증 없이 시간당 60회 제한. 403 발생 시 에러 UI 필수 | API 남용 |
| **보너스 과제** | 프로젝트 필터링, 타이핑 효과, Formspree 연동, 시스템 다크모드 감지 (선택) | — |

---

## 3. 기능 요구사항 상세 명세

### 3-1. 프로젝트 기본 구성

**폴더 구조 (의무 준수):**
```
B1-1/
├── index.html           ← 메인 페이지 (시맨틱 마크업)
├── css/
│   └── style.css        ← 외부 스타일시트 (CSS Variables 포함)
├── js/
│   ├── main.js          ← 초기화 및 전역 이벤트
│   ├── api.js           ← GitHub API 비동기 통신
│   ├── ui.js            ← DOM 조작 및 카드 렌더링
│   └── events.js        ← 폼 유효성 검사 및 이벤트 바인딩
├── images/              ← 이미지 자산
├── README.md
├── TASK_SPECIFICATION.md
└── STEP_BY_STEP_EXECUTION_AND_TEST_GUIDE.md
```

---

### 3-2. HTML 구조 (시맨틱 마크업)

**의무 섹션 구성:**

| 섹션 | 구현 내용 | HTML 태그 |
| :--- | :--- | :--- |
| Header/Nav | 로고(왼쪽) + 메뉴(오른쪽) + 다크모드 토글 버튼 | `<header>`, `<nav>` |
| Hero | 인사말 + CTA 버튼 (View Projects, Contact) | `<section id="hero">` |
| About | 자기소개 + 프로필 이미지 | `<section id="about">` |
| Skills | 기술 스택 카드/배지 목록 | `<section id="skills">` |
| Projects | GitHub API 연동 카드 | `<section id="projects">` |
| Contact | 이름/이메일/메시지 폼 | `<section id="contact">` |
| Footer | 저작권 + 소셜 링크 | `<footer>` |

---

### 3-3. CSS 스타일링

**의무 구현 항목:**
- `css/style.css` 단독 외부 스타일시트
- CSS Variables 정의:
  ```css
  :root {
    --color-primary: ...;
    --color-bg: ...;
    --color-text: ...;
    --font-main: ...;
    --spacing-md: ...;
  }
  [data-theme="dark"] {
    --color-bg: ...;
    --color-text: ...;
  }
  ```
- 모바일 퍼스트 미디어 쿼리 (768px 태블릿, 1024px 데스크톱)
- 네비게이션: `Flexbox` (로고 왼쪽, 메뉴 오른쪽)
- Projects 카드: `Grid` (`auto-fit, minmax()`)
- hover 효과 + transition, box-shadow 적용

---

### 3-4. JavaScript 인터랙션 (6가지 필수 기능)

| 기능 | 트리거 | 구현 로직 | 판정 기준 |
| :--- | :--- | :--- | :--- |
| 햄버거 메뉴 토글 | 모바일에서 햄버거 버튼 클릭 | `classList.toggle('active')` | 메뉴 표시/숨김 반복 |
| 부드러운 스크롤 | 네비게이션 링크 클릭 | `scroll-behavior: smooth` 또는 `scrollIntoView()` | 해당 섹션으로 이동 |
| 스크롤 TOP 버튼 | 스크롤 300px 이상 | `window.scrollY > 300` → 버튼 표시 | 버튼 클릭 시 top 이동 |
| 네비게이션 스타일 | 스크롤 60px 이상 | `classList.add('scrolled')` | 배경색 변경 확인 |
| 다크 모드 | 토글 버튼 클릭 | `document.documentElement.dataset.theme` + `localStorage` | 새로고침 후 유지 |
| 스크롤 애니메이션 | 섹션 뷰포트 진입 | `IntersectionObserver` threshold 0.2 | 요소 fade-in 확인 |

---

### 3-5. Contact 폼 유효성 검사

**의무 구현:**
- 필드: 이름(name), 이메일(email), 메시지(message)
- 검증 규칙:
  - 빈 필드 제출 불가
  - 이메일 형식 검증 (정규식: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`)
  - 에러 메시지: 해당 입력 필드 바로 아래 표시
- 성공 처리: `event.preventDefault()` + "감사합니다" 성공 메시지 표시

---

### 3-6. GitHub API 연동 (4가지 상태 UI)

**API 엔드포인트:**
```
GET https://api.github.com/users/{GITHUB_USERNAME}/repos?sort=updated&per_page=6
```

**의무 구현 4가지 상태:**

| 상태 | 트리거 | UI 표현 |
| :--- | :--- | :--- |
| **로딩** | API 요청 중 | 스피너 SVG 또는 "로딩 중..." 텍스트 |
| **성공** | 응답 정상 수신 | 카드 리스트 렌더링 (map으로 HTML 생성) |
| **에러** | 네트워크 오류 또는 403 | "프로젝트를 불러올 수 없습니다" + 재시도 버튼 |
| **빈 상태** | repos 배열이 빈 경우 | "표시할 프로젝트가 없습니다" |

**카드에 표시할 데이터:** 저장소 이름, 설명, 언어, ⭐ Star 수, 🍴 Fork 수, GitHub 링크

---

### 3-7. 상태 관리 패턴 (최소 3가지 이상)

**"이벤트 → 상태 변경 → 화면 업데이트" 흐름 3가지:**
1. 다크 모드 토글 → `isDarkMode` 상태 변경 → 전체 화면 스타일 변경
2. API 호출 → `{status: 'loading'|'success'|'error'|'empty'}` 상태 변경 → Projects 섹션 렌더링 변경
3. 폼 입력 → `{isValid: boolean}` 상태 변경 → 에러 메시지 표시/숨김

---

### 3-8. 배포 (GitHub Pages)

- GitHub Pages로 배포
- 배포 URL에서 모든 기능 정상 동작 (반응형, 인터랙션, API 연동, 폼 검증)
- README에 포함 필수:
  - 프로젝트 설명
  - 사용 기술 스택
  - 배포 URL
  - 데스크톱/모바일/다크모드 스크린샷

---

## 4. 최종 결과물 규격

| 항목 | 규격 |
| :--- | :--- |
| 파일 수 | index.html + css/style.css + js/4개 파일 최소 |
| 섹션 수 | 6개 (Hero, About, Skills, Projects, Contact, Footer) |
| 인터랙션 수 | 6가지 이상 (햄버거, 스크롤, TOP, 네비스타일, 다크모드, 애니메이션) |
| API 상태 수 | 4가지 (로딩, 성공, 에러, 빈) |
| 폼 검증 수 | 최소 3개 규칙 (빈값, 이메일 형식, 성공 메시지) |
| 반응형 브레이크포인트 | 768px, 1024px |
| 배포 환경 | GitHub Pages |
| 브라우저 지원 | 최신 Chrome |
