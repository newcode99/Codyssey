# 🎓 B1-1 포트폴리오 웹사이트 공식 평가 항목 원본 질문별 코드 & 연계성 마스터 가이드

> **"체크리스트의 원본 질문 텍스트 그대로 1:1 매칭!"**  
> 본 가이드는 평가표의 공식 질문 텍스트를 원문 그대로 기재하고, 각 질문에 대해 **실제 프로젝트 소스 코드**, **모듈 간의 상호작용(연계성)**, 그리고 **면접관/평가관 앞에서의 명쾌한 모범 답변**을 완벽하게 제시합니다.

---

# 🏛️ 제2장. 구현 구조 설명

---

### [질문 2-1] HTML, CSS, JavaScript가 각각의 파일로 분리되어 있고, 분리한 이유와 각 파일의 역할을 설명할 수 있는가?

#### 1. 비즈니스 설계 의도 및 분리 이유 (Description)
* **분리한 이유 (관심사의 분리, Separation of Concerns)**:
  * 하나의 파일 안에 구조(HTML), 디자인(CSS), 로직(JS)을 모두 집어넣으면 코드 길이가 수천 줄로 비대해져 유지보수가 불가능해집니다.
  * 파일을 엄격히 분리함으로써 HTML은 '문서의 뼈대', CSS는 '시각적 스타일', JS는 '동적 인터랙션 및 통신'이라는 단일 책임을 갖게 되며, 브라우저가 CSS와 JS 파일을 개별 캐싱(Caching)하여 재방문 시 로딩 속도가 극대화됩니다.

#### 2. 실제 프로젝트 파일 구조 및 모듈 역할

```
B1-1/
├── index.html           ← 뷰 계층 (시맨틱 골격 및 컨테이너 제공)
├── css/
│   └── style.css        ← 스타일 계층 (디자인 토큰, 테마, 모바일 퍼스트 레이아웃)
└── js/
    ├── main.js          ← 오케스트레이터 (초기화, 테마/스크롤 지휘, 모듈 조립)
    ├── api.js           ← 네트워크 계층 (GitHub REST API 통신 및 데이터 가드레일)
    ├── ui.js            ← 렌더링 계층 (XSS 새니타이징 및 순수 DOM 카드 렌더링)
    └── events.js        ← 컨트롤러 계층 (Contact 폼 정규식 검증 및 submit 차단)
```

#### 3. 모듈 간 연계성 코드 분석 ([main.js](file:///Users/hwangjeonghyeon/codyssey_2026/2-1/B1-1/js/main.js#L6-L20))
```javascript
// B1-1/js/main.js - 각 모듈을 임포트하여 조립하는 최상위 오케스트레이터
import { fetchGitHubRepos } from './api.js';      // 네트워크 모듈 연결
import { renderLoading, renderProjectCards } from './ui.js'; // 뷰 렌더러 모듈 연결
import { initContactForm } from './events.js';    // 이벤트 컨트롤러 모듈 연결

document.addEventListener('DOMContentLoaded', () => {
  initThemeManager();                             // main.js 자체 테마 관리
  initProjectsSection();                          // api.js + ui.js 결합 실행
  initContactForm(document.querySelector('#contact-form')); // events.js 위임
});
```

---

### [질문 2-2] header, nav, main, section, footer 등 시맨틱 태그를 사용했고, 어떤 기준으로 태그를 선택했는지 설명할 수 있는가?

#### 1. 시맨틱(Semantic) 태그의 정의와 선택 기준 (Description)
* **시맨틱이란**: '의미가 있는' 태그를 뜻합니다. 단순히 영역만 나누는 `<div>`와 달리, 태그 이름 자체로 브라우저와 검색 엔진에게 해당 구역의 비즈니스 목적을 알려줍니다.
* **태그 선택 기준**:
  * `<header>` & `<nav>`: 사이트의 최상단 식별 로고와 페이지 내 주요 섹션으로 이동하는 네비게이션 링크 묶음에 적용.
  * `<main>`: 문서 전체에서 단 하나만 존재하는 핵심 콘텐츠 본문 전체를 감싸는 용도.
  * `<section>`: 반드시 독립적인 제목(`<h2>`)을 가지며, 하나의 완성된 주제(About, Skills, Projects, Contact)를 다루는 구획.
  * `<article>`: 문서 내에서 따로 떼어내어 RSS 피드나 카드 갤러리로 독립 배포해도 온전한 의미를 갖는 개별 프로젝트 카드 단위에 적용.
  * `<footer>`: 저작권, 소셜 링크, 사이트 하단 메타 정보를 담는 마감 구획.

#### 2. 실제 프로젝트 코드 ([index.html](file:///Users/hwangjeonghyeon/codyssey_2026/2-1/B1-1/index.html#L35-L95))
```html
<!-- B1-1/index.html (시맨틱 구획 발췌) -->
<header id="header" class="site-header">
  <div class="container nav-container">
    <a href="#hero" class="brand-logo">&lt;/&gt; PORTFOLIO</a>
    <nav id="nav-menu" class="nav-menu" aria-label="메인 네비게이션">
      <ul class="nav-list">
        <li><a href="#projects" class="nav-link">Projects</a></li>
      </ul>
    </nav>
  </div>
</header>

<main id="main-content">
  <section id="projects" class="projects-section section animate-on-scroll">
    <div class="container">
      <h2 class="section-title">GitHub 연동 라이브 프로젝트</h2>
      <div id="projects-container" class="projects-container"></div>
    </div>
  </section>
</main>
```

#### 3. 모듈 간 연계성 분석
* **JS Scrollspy 연계**: `main.js`의 `initNavigationManager()`는 `document.querySelectorAll('section[id]')`를 순회하며, 스크롤 위치가 해당 `<section>` 내에 진입할 때마다 상단 `<nav>`의 `<a href="#id">` 링크에 `.active` 클래스를 실시간 동기화합니다.

---

### [질문 2-3] CSS 변수로 색상, 폰트 등을 정의했고, 변수로 관리하면 어떤 이점이 있는지 설명할 수 있는가?

#### 1. 개념 및 변수 관리의 이점 (Description)
* **CSS Variables (`var(--...)`)의 3대 이점**:
  1. **단일 진실 공급원(SSOT)**: 메인 테마 색상을 바꿀 때 수백 개의 CSS 선언을 일일이 수정할 필요 없이 `:root`의 `--primary` 값 하나만 수정하면 사이트 전체에 자동 반영됩니다.
  2. **다크 모드 구현 극대화**: HTML 구조나 자바스크립트 변경 없이, `[data-theme="dark"]` 선택자 아래에서 변수 값만 갈아 끼우면 사이트 전체의 색조가 한 번에 전환됩니다.
  3. **코드 가독성 향상**: `#0ea5e9`라는 난해한 16진수 코드 대신 `var(--primary)`라는 명확한 의미의 이름을 사용하여 팀 협업 생산성을 높입니다.

#### 2. 실제 프로젝트 코드 ([css/style.css](file:///Users/hwangjeonghyeon/codyssey_2026/2-1/B1-1/css/style.css#L15-L55))
```css
/* B1-1/css/style.css */
:root {
  --primary: #0ea5e9;           /* 메인 액센트 블루 */
  --bg-primary: #f8fafc;        /* 밝은 라이트 배경 */
  --bg-card: #ffffff;           /* 순백색 카드 */
  --text-primary: #0f172a;      /* 고대비 텍스트 */
  --font-heading: 'Outfit', sans-serif;
}

/* 다크 모드 활성화 시 CSS 엔진이 자동으로 변수 값만 오버라이드 */
[data-theme="dark"] {
  --primary: #38bdf8;
  --bg-primary: #0f172a;        /* 딥 다크 배경 */
  --bg-card: #1e293b;           /* 입체감 있는 다크 카드 */
  --text-primary: #f8fafc;
}

.project-card {
  background: var(--bg-card);   /* 테마에 따라 자동 전환 */
  color: var(--text-primary);
  border: 1px solid var(--border-light);
}
```

#### 3. 모듈 간 연계성 분석
* **JS 테마 스위처 연계**: `main.js`의 `applyTheme(activeTheme)` 함수가 실행되면 DOM의 루트 요소에 `document.documentElement.dataset.theme = 'dark'`를 설정합니다. 그러면 CSS 엔진이 즉시 `[data-theme="dark"]` 블록을 활성화하여 모든 자식 컴포넌트의 테마를 재렌더링합니다.

---

### [질문 2-4] onclick 속성 대신 addEventListener를 사용한 이유를 설명할 수 있는가?

#### 1. 개념 및 비교 우위 (Description)
* **HTML 인라인 `onclick="..."`의 치명적 결함**:
  * 마크업과 로직이 뒤섞여 관심사의 분리가 깨집니다.
  * 동일한 요소에 2개 이상의 핸들러를 등록할 수 없으며(기존 함수를 덮어씀), 전역 스코프를 오염시켜 XSS 공격에 취약해집니다.
* **`addEventListener`를 채택한 이유**:
  * 하나의 요소에 여러 개의 독립된 이벤트 리스너를 누적 등록할 수 있습니다.
  * 이벤트 버블링(Bubbling)과 캡처링(Capturing) 단계를 제어할 수 있으며, 필요 시 `removeEventListener`로 메모리 누수를 방지할 수 있습니다.

#### 2. 실제 프로젝트 코드 ([js/main.js](file:///Users/hwangjeonghyeon/codyssey_2026/2-1/B1-1/js/main.js#L35-L40))
```javascript
// B1-1/js/main.js (순수 addEventListener 기반 바인딩)
const themeToggleBtn = document.querySelector('#theme-toggle-btn');
if (themeToggleBtn) {
  themeToggleBtn.addEventListener('click', () => {
    const activeTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
    applyTheme(activeTheme);
    localStorage.setItem('theme', activeTheme);
  });
}
```

---

# ⚙️ 제3장. 코드 동작 원리 (이벤트 & 렌더링)

---

### [질문 3-1] 다크 모드, API 호출, 폼 유효성 검사 중 하나를 골라, "이벤트 → 상태 변경 → 화면 업데이트" 흐름이 코드에서 어떻게 이어지는지 설명할 수 있는가?

#### 1. 선택 항목: GitHub API Projects 영역의 4대 상태 머신 라이프사이클
* **설계 흐름**:
  1. **사용자 이벤트 (Event)**: 상태 제어 버튼 클릭 또는 페이지 초기 로드.
  2. **상태 변경 (State Mutation)**: 내부 상태 변수 `currentState = 'loading' | 'success' | 'error' | 'empty'` 전이.
  3. **화면 업데이트 (DOM Re-render)**: 상태에 해당하는 전용 뷰 렌더러 함수 호출.

#### 2. 실제 코드 흐름 추적 ([js/main.js](file:///Users/hwangjeonghyeon/codyssey_2026/2-1/B1-1/js/main.js#L191-L243))
```javascript
// B1-1/js/main.js
async function applyState(state, forceReload = false) {
  // [1단계: 상태 변경 및 탭 하이라이트 동기화]
  updateActiveButton(state);

  // [2단계: 상태 머신 분기 처리]
  switch (state) {
    case 'loading':
      renderLoading(container); // [3단계: DOM 업데이트 - 스피너 렌더링]
      break;

    case 'error':
      renderError(              // [3단계: DOM 업데이트 - 에러 박스 및 재시도 버튼]
        container,
        'GitHub API 호출 한도 초과(403) 또는 네트워크 오류',
        () => applyState('success', true), // 재시도 이벤트 연결
        () => renderProjectCards(container, MOCK_FALLBACK_REPOS)
      );
      break;

    case 'success':
    default:
      renderLoading(container);
      const result = await fetchGitHubRepos('newcode99', 6);
      if (result.status === 'SUCCESS') {
        renderProjectCards(container, result.data); // [3단계: DOM 업데이트 - 6개 카드 렌더링]
      }
      break;
  }
}
```

---

### [질문 3-2] async/await와 try/catch를 사용하여 API 호출 성공과 실패를 어떻게 분기 처리했는지 설명할 수 있는가?

#### 1. 비동기 예외 처리 및 가드레일 설계 (Description)
* 네트워크 통신은 언제든 실패(403, 404, 500, 오프라인)할 수 있습니다. `try/catch` 블록으로 `fetch()`를 감싸지 않으면 에러 발생 시 자바스크립트 엔진 전체가 멈추고 콘솔에 붉은 에러가 뜹니다.
* 우리 코드는 HTTP 응답 상태 코드(403 등)와 네트워크 예외를 모두 캐치하여, 상위 호출자(`main.js`)에게 항상 일관된 규격의 상태 객체 `{ status, data, error }`를 반환하도록 캡슐화했습니다.

#### 2. 실제 프로젝트 코드 ([js/api.js](file:///Users/hwangjeonghyeon/codyssey_2026/2-1/B1-1/js/api.js#L40-L75))
```javascript
// B1-1/js/api.js
export async function fetchGitHubRepos(username, limit = 6) {
  const url = `https://api.github.com/users/${encodeURIComponent(username)}/repos?sort=updated&per_page=${limit}`;

  try {
    const response = await fetch(url);

    // 403 Rate Limit 한도 초과 분기
    if (response.status === 403) {
      return { status: API_STATUS.ERROR, error: 'GitHub API 호출 한도(시간당 60회)를 초과했습니다.' };
    }
    // 기타 HTTP 에러 분기
    if (!response.ok) {
      return { status: API_STATUS.ERROR, error: `서버 응답 오류 (HTTP ${response.status})` };
    }

    const repos = await response.json();
    if (repos.length === 0) {
      return { status: API_STATUS.EMPTY, data: [] }; // 빈 상태 분기
    }

    return { status: API_STATUS.SUCCESS, data: sanitizeData(repos) }; // 성공 분기

  } catch (err) {
    // 네트워크 단절 및 DNS 실패 분기
    return { status: API_STATUS.ERROR, error: '인터넷 연결이 끊겼거나 일시적인 통신 장애입니다.' };
  }
}
```

---

### [질문 3-3] map, filter 등 배열 메서드를 활용하여 GitHub 데이터를 카드 UI로 변환하는 과정을 설명할 수 있는가?

#### 1. 선언형 데이터 변환 파이프라인 (Description)
* 명령형 `for` 문 대신 `Array.prototype.map()`을 사용하여, 서버에서 넘어온 원본 데이터 객체 배열을 순수 함수 형태로 순회하며 각 원소를 HTML 문자열 카드 블록으로 1:1 매핑 변환합니다.
* 변환된 문자열 배열은 `.join('')`을 거쳐 단 하나의 통합 HTML 스트링으로 결합된 후, 단 1회의 `innerHTML` 조작으로 DOM 트리에 마운트됩니다 (불필요한 DOM Reflow 억제).

#### 2. 실제 프로젝트 코드 ([js/ui.js](file:///Users/hwangjeonghyeon/codyssey_2026/2-1/B1-1/js/ui.js#L89-L132))
```javascript
// B1-1/js/ui.js
export function renderProjectCards(container, repos) {
  if (!container || !Array.isArray(repos)) return;

  // map 메서드를 통해 순수 자바스크립트 객체 배열 -> HTML 카드 배열로 변환
  const cardsMarkup = repos.map(repo => {
    // XSS 방어를 위한 이스케이프 선행 처리
    const safeName = escapeHTML(repo.name);
    const safeDesc = escapeHTML(repo.description);
    const safeLang = escapeHTML(repo.language);
    const safeUrl = escapeHTML(repo.url);

    return `
      <article class="project-card" data-id="${repo.id}">
        <div class="card-header">
          <i class="fa-regular fa-folder-closed folder-icon"></i>
          <a href="${safeUrl}" target="_blank" rel="noopener noreferrer"><i class="fa-solid fa-arrow-up-right-from-square"></i></a>
        </div>
        <h3 class="card-title">${safeName}</h3>
        <p class="card-desc">${safeDesc}</p>
        <div class="card-footer">
          <span class="card-lang">${safeLang}</span>
          <span><i class="fa-regular fa-star"></i> ${repo.stars}</span>
        </div>
      </article>
    `;
  }).join(''); // 배열 요소들을 하나의 긴 HTML 문자열로 결합

  // 단 1회의 DOM 트리에 주입 (Reflow 최소화)
  container.innerHTML = `<div class="projects-grid">${cardsMarkup}</div>`;
}
```

---

### [질문 3-4] Flexbox와 Grid를 각각 어디에 썼고, 왜 그 방식을 선택했는지 설명할 수 있는가?

#### 1. 레이아웃 엔진 선정 기준 (Description)
* **Flexbox (1차원 레이아웃 엔진)**:
  * 요소들을 **가로(Row) 또는 세로(Column)** 중 단 하나의 축을 기준으로 배치할 때 최적입니다.
  * **적용 위치**: 상단 네비게이션 헤더(`.nav-container`), 카드 상단 아이콘 정렬(`.card-header`), 카드 푸터 통계 배지(`.card-footer`).
  * **선택 이유**: 로고는 왼쪽, 메뉴는 오른쪽에 두고 수직 중앙 정렬(`align-items: center; justify-content: space-between;`)을 수행하는 데 가장 유연하기 때문입니다.
* **CSS Grid (2차원 레이아웃 엔진)**:
  * 요소들을 **가로 행(Row)과 세로 열(Column)** 을 동시에 고려하여 바둑판 형태로 배치할 때 필수적입니다.
  * **적용 위치**: GitHub 프로젝트 카드 갤러리(`.projects-grid`), 보유 기술 카테고리(`.skills-category-grid`).
  * **선택 이유**: 화면 폭에 따라 1열 ➡️ 2열 ➡️ 3열로 열 개수를 균등 분할하고 각 카드의 높이를 자동으로 통일하는 데 Grid가 압도적으로 효율적이기 때문입니다.

#### 2. 실제 프로젝트 비교 코드 ([css/style.css](file:///Users/hwangjeonghyeon/codyssey_2026/2-1/B1-1/css/style.css#L310-L755))
```css
/* B1-1/css/style.css */

/* 1. Flexbox: 1차원 수평 정렬 헤더 */
.nav-container {
  display: flex;
  align-items: center;
  justify-content: space-between; /* 양 끝 정렬 */
}

/* 2. Grid: 2차원 반응형 바둑판 카드 목록 */
.projects-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.75rem;
}
@media (min-width: 1024px) {
  .projects-grid {
    grid-template-columns: repeat(3, 1fr); /* 가로 3열 균등 분할 */
  }
}
```

---

# 🛡️ 제4장. 심화 질문 (아키텍처 & 최적화)

---

### [질문 4-1] 상태 객체를 따로 만들어서 관리한 이유는 무엇인가? (그냥 변수로 쓰면 안 되는가?)

#### 1. 개념 및 상태 객체 패턴의 필요성 (Description)
* **그냥 개별 변수로 썼을 때의 위험**:
  * 만약 `let isLoading = false; let isError = false; let isSuccess = false;` 처럼 독립된 boolean 변수를 남발하면, `isLoading = true`인데 동시에 `isError = true`가 되는 **불가능한 모순 상태(Impossible State)** 가 발생하여 화면이 꼬이게 됩니다.
* **상태 객체(`API_STATUS`)로 관리한 이유**:
  * 상태를 단 하나의 열거형 상수로 정의함으로써, 시스템이 특정 시점에 오직 단 하나의 상태(`LOADING`, `SUCCESS`, `ERROR`, `EMPTY`)만 가질 수 있도록 **상태 머신(Finite State Machine)** 을 보장합니다.
  * 휴먼 에러(오타)를 컴파일/런타임 단계에서 방지하고 상태 전이의 흐름을 예측 가능하게 만듭니다.

#### 2. 실제 프로젝트 코드 ([js/api.js](file:///Users/hwangjeonghyeon/codyssey_2026/2-1/B1-1/js/api.js#L6-L12))
```javascript
// B1-1/js/api.js (단일 진실 공급원 상태 객체)
export const API_STATUS = {
  IDLE: 'IDLE',
  LOADING: 'LOADING',
  SUCCESS: 'SUCCESS',
  ERROR: 'ERROR',
  EMPTY: 'EMPTY'
};
```

---

### [질문 4-2] 반응형 디자인에서 "모바일 퍼스트"로 작성한 이유는 무엇인가?

#### 1. 모바일 퍼스트(Mobile-First) 채택의 기술적 근거 (Description)
* **성능 최적화**:
  * 스마트폰은 데스크톱보다 CPU 성능과 네트워크 대역폭이 제한적입니다.
  * 데스크톱용 무거운 스타일을 먼저 로드하고 모바일에서 `display: none`으로 가리거나 덮어쓰는(Desktop-First) 방식은 모바일 기기에 막대한 렌더링 낭비를 초래합니다.
* **진보적 향상 (Progressive Enhancement)**:
  * 모바일 기준의 최소한의 필수 코드를 기본 스타일로 탑재하고, 화면이 넓어질 때만 `@media (min-width: ...)`로 레이아웃을 점진적으로 확장하여, 저사양 디바이스에서도 가장 빠르고 쾌적한 렌더링 성능을 보장합니다.

#### 2. 실제 프로젝트 코드 ([css/style.css](file:///Users/hwangjeonghyeon/codyssey_2026/2-1/B1-1/css/style.css))
```css
/* 기본 스타일 (모바일 우선: 1열) */
.skills-category-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
}

/* 태블릿 이상으로 확장 (min-width) */
@media (min-width: 768px) {
  .skills-category-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

/* 데스크톱 이상으로 확장 (min-width) */
@media (min-width: 1024px) {
  .skills-category-grid {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

---

## 🏆 결론 및 면접 대비 요약
본 가이드에 수록된 질문들은 실제 웹 프론트엔드 실기 평가 및 기술 면접에서 가장 핵심적으로 다루어지는 표준 질문들입니다. 각 질문에 대해 위와 같이 **"왜 그렇게 설계했는지(의도) → 실제 코드의 어느 부분인지(근거) → 다른 모듈과 어떻게 맞물리는지(연계성)"** 의 3박자를 갖추어 답변하시면 완벽한 만점을 획득하실 수 있습니다!
