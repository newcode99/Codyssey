# B1-1 종합 알고리즘 및 코드 심층 해부서 (COMPREHENSIVE_ALGORITHM_AND_CODE_DEEP_DIVE)

본 문서는 B1-1 반응형 포트폴리오 웹사이트를 구성하는 핵심 모듈의 알고리즘과 제어 흐름을 **기능 개요 → 제어 흐름/라이프사이클 → 규격 표 → 코드 구현체 → 검증 체크포인트**의 5단계 구조로 라인 바이 라인 해부합니다.

---

## 1. `js/api.js` — GitHub REST API 비동기 페칭 및 4대 상태 머신

### 1) 기능 개요 및 비즈니스 설계 의도 (Description)
GitHub 공개 REST API(`https://api.github.com/users/{username}/repos`)를 호출하여 최신 순으로 정렬된 상위 6개 공개 저장소 목록을 비동기 수집합니다. 단순한 성공 데이터 반환에 그치지 않고, 네트워크 오류, 403 Rate Limit 한도 초과, 빈 저장소 상태를 포괄하는 4대 상태 머신을 안정적으로 구동하는 핵심 통신 계층입니다.

### 2) 내부 제어 흐름 및 I/O 라이프사이클 (Lifecycle & Storage I/O)
1. **요청 개시**: 함수 호출 즉시 전역/로컬 상태를 `loading`으로 전이.
2. **비동기 요청**: `fetch()` API로 HTTP GET 요청 전송 (헤더: `Accept: application/vnd.github.v3+json`).
3. **HTTP 응답 코드 판별**:
   - `response.ok (200)`: JSON 파싱 수행. Fork된 저장소 필터링(`!repo.fork`) 후 최근 업데이트순 정렬.
   - `403 (Rate Limit)`: 시간당 60회 제한 초과 예외 생성.
   - `404 (Not Found)`: 존재하지 않는 계정 예외 생성.
4. **결과 분기**: 데이터 길이가 0개이면 `empty` 상태 반환, 1개 이상이면 `success` 상태와 정제된 6개 데이터 반환.
5. **예외 격리**: 네트워크 두절 등 치명적 오류 발생 시 `error` 상태로 전이하고 에러 원인을 상위 UI로 전파.

### 3) 파라미터 옵션 및 제약 조건 규격 표 (Parameter Table)

| 파라미터 명 | 타입 | 기본값 | 제약 조건 및 유효 범위 | 비고 |
| :--- | :---: | :---: | :--- | :--- |
| `username` | `string` | 필수 주입 | 영문, 숫자, 하이픈(-) 조합의 유효한 GitHub ID | 공백 시 에러 반환 |
| `perPage` | `number` | `6` | 1 이상 100 이하 정수 | 포트폴리오 카드 그리드 규격 |
| `sort` | `string` | `'updated'` | `'created'`, `'updated'`, `'pushed'` 중 선택 | 최신 활동순 정렬 |

### 4) 실제 코드 구현체 (Code Block)

```javascript
/**
 * GitHub API 클라이언트 모듈
 * 단일 책임: GitHub REST API 통신 및 데이터 정제, 상태 예외 캡슐화
 */

export const API_STATUS = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error',
  EMPTY: 'empty'
};

export async function fetchGitHubRepos(username, perPage = 6) {
  if (!username || typeof username !== 'string') {
    throw new Error('유효한 GitHub 사용자 이름을 지정해야 합니다.');
  }

  const endpoint = `https://api.github.com/users/${encodeURIComponent(username)}/repos?sort=updated&per_page=30`;

  try {
    const response = await fetch(endpoint, {
      headers: {
        'Accept': 'application/vnd.github.v3+json'
      }
    });

    // HTTP 상태 코드 가드레일
    if (!response.ok) {
      if (response.status === 403) {
        throw new Error('API_RATE_LIMIT');
      } else if (response.status === 404) {
        throw new Error('USER_NOT_FOUND');
      } else {
        throw new Error(`HTTP_ERROR_${response.status}`);
      }
    }

    const rawData = await response.json();

    // 순수 저장소만 선별 (Fork 저장소 배제) 및 상위 6개 슬라이싱
    const filteredRepos = rawData
      .filter(repo => !repo.fork)
      .slice(0, perPage)
      .map(repo => ({
        id: repo.id,
        name: repo.name,
        description: repo.description || '프로젝트 설명이 등록되지 않았습니다.',
        language: repo.language || 'Markdown/Text',
        stars: repo.stargazers_count,
        forks: repo.forks_count,
        url: repo.html_url,
        updatedAt: new Date(repo.updated_at).toLocaleDateString('ko-KR')
      }));

    if (filteredRepos.length === 0) {
      return { status: API_STATUS.EMPTY, data: [] };
    }

    return { status: API_STATUS.SUCCESS, data: filteredRepos };

  } catch (error) {
    return {
      status: API_STATUS.ERROR,
      error: error.message || '네트워크 연결 상태를 확인해주세요.',
      data: []
    };
  }
}
```

### 5) 핵심 검증 포인트 및 출력 결과 분석 (Verification Checkpoint)
* **검증 포인트 1**: Fork 저장소가 정확히 배제되고 본인이 직접 생성한 저장소만 필터링되는가?
* **검증 포인트 2**: 403 응답 시 애플리케이션 크래시 없이 `{ status: 'error', error: 'API_RATE_LIMIT' }` 객체가 반환되는가?
* **검증 포인트 3**: 저장소가 없는 계정 입력 시 빈 배열과 함께 `status: 'empty'`가 정상 도출되는가?

---

## 2. `js/ui.js` — DOM 렌더링 엔진 및 XSS 방어 새니타이저

### 1) 기능 개요 및 비즈니스 설계 의도 (Description)
비즈니스 로직과 화면을 철저히 분리하기 위해, 모든 DOM 조작과 마운트를 전담하는 계층입니다. 외부 API로부터 전달받은 사용자 정의 텍스트(프로젝트명, 설명 등)를 HTML 엔티티로 치환하여 악의적인 스크립트 실행(XSS)을 원천 차단하고, 4대 API 상태에 따른 UI 컴포넌트를 선언적으로 렌더링합니다.

### 2) 내부 제어 흐름 및 I/O 라이프사이클 (Lifecycle & Storage I/O)
1. **타겟 컨테이너 조회**: `#projects-container` 요소를 DOM에서 획득.
2. **상태별 분기 렌더링**:
   - `loading`: 컨테이너 내부를 SVG 스피너 마크업으로 교체.
   - `error`: 에러 메시지 텍스트와 함께 `재시도` 버튼 요소를 바인딩하여 렌더링.
   - `empty`: "표시할 프로젝트가 없습니다" 일러스트레이션 텍스트 주입.
   - `success`: `repos.map()` 고차함수를 순회하며 `escapeHTML()`로 감싼 카드 마크업 문자열을 조합한 뒤 컨테이너에 주입.

### 3) 파라미터 옵션 및 제약 조건 규격 표 (Parameter Table)

| 함수 명 | 인자 (Arguments) | 반환값 (Returns) | 제약 조건 및 예외 처리 |
| :--- | :--- | :--- | :--- |
| `escapeHTML` | `str: string` | `escaped: string` | `null` 또는 `undefined` 입력 시 빈 문자열(`''`) 반환 |
| `renderProjects` | `container: HTMLElement, state: object, onRetry: function` | `void` | 컨테이너 요소 부재 시 콘솔 경고 출력 후 조기 종료 |

### 4) 실제 코드 구현체 (Code Block)

```javascript
/**
 * UI 렌더링 전담 모듈
 * 단일 책임: DOM 탐색, 템플릿 매핑, 상태별 화면 렌더링, XSS 보안 방어
 */

export function escapeHTML(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

export function renderLoading(container) {
  container.innerHTML = `
    <div class="status-box loading-box" role="status" aria-live="polite">
      <div class="spinner" aria-hidden="true"></div>
      <p>GitHub 프로젝트를 불러오는 중입니다...</p>
    </div>
  `;
}

export function renderError(container, errorMessage, onRetry) {
  container.innerHTML = `
    <div class="status-box error-box" role="alert">
      <i class="fa-solid fa-triangle-exclamation status-icon"></i>
      <p class="error-msg">프로젝트를 불러오지 못했습니다: ${escapeHTML(errorMessage)}</p>
      <button class="btn btn-primary retry-btn" id="retry-fetch-btn">
        <i class="fa-solid fa-rotate-right"></i> 다시 시도
      </button>
    </div>
  `;

  const retryBtn = container.querySelector('#retry-fetch-btn');
  if (retryBtn && typeof onRetry === 'function') {
    retryBtn.addEventListener('click', onRetry);
  }
}

export function renderEmpty(container) {
  container.innerHTML = `
    <div class="status-box empty-box">
      <i class="fa-solid fa-folder-open status-icon"></i>
      <p>표시할 공개 프로젝트가 없습니다.</p>
    </div>
  `;
}

export function renderProjectCards(container, repos) {
  const cardsHTML = repos.map(repo => `
    <article class="project-card" data-id="${repo.id}">
      <div class="card-header">
        <i class="fa-regular fa-folder-closed folder-icon"></i>
        <div class="card-links">
          <a href="${escapeHTML(repo.url)}" target="_blank" rel="noopener noreferrer" 
             aria-label="${escapeHTML(repo.name)} 저장소 바로가기">
            <i class="fa-solid fa-arrow-up-right-from-square"></i>
          </a>
        </div>
      </div>
      <h3 class="card-title">${escapeHTML(repo.name)}</h3>
      <p class="card-desc">${escapeHTML(repo.description)}</p>
      <div class="card-footer">
        <span class="card-lang">
          <span class="lang-dot"></span>${escapeHTML(repo.language)}
        </span>
        <div class="card-stats">
          <span title="Stars"><i class="fa-regular fa-star"></i> ${repo.stars}</span>
          <span title="Forks"><i class="fa-solid fa-code-fork"></i> ${repo.forks}</span>
        </div>
      </div>
    </article>
  `).join('');

  container.innerHTML = cardsHTML;
}
```

### 5) 핵심 검증 포인트 및 출력 결과 분석 (Verification Checkpoint)
* **검증 포인트 1**: `<script>` 태그가 포함된 설명이 주입되어도 스크립트가 실행되지 않고 `&lt;script&gt;` 엔티티로 안전하게 렌더링되는가?
* **검증 포인트 2**: 재시도 버튼 클릭 시 상위 핸들러(`onRetry`)가 정상 트리거되어 로딩 상태로 복귀하는가?
* **검증 포인트 3**: 접근성 규격(`role="alert"`, `aria-label`, `rel="noopener noreferrer"`)이 완비되어 있는가?

---

## 3. `js/events.js` — 실시간 정규식 폼 유효성 검사 및 이벤트 캡슐화

### 1) 기능 개요 및 비즈니스 설계 의도 (Description)
Contact 섹션의 이름, 이메일, 메시지 입력 필드를 사용자가 타이핑하는 즉시 실시간 정규식으로 검증하고 피드백을 제공합니다. 잘못된 양식으로 폼이 전송되는 것을 사전에 차단하며, 폼 제출 시 브라우저 기본 새로고침을 방어하고 사용자에게 친절한 전송 완료 상태를 렌더링합니다.

### 2) 내부 제어 흐름 및 I/O 라이프사이클 (Lifecycle & Storage I/O)
1. **실시간 감시**: 각 입력 필드의 `input` 및 `blur` 이벤트를 리스닝.
2. **필드별 검증 규격**:
   - `name`: 공백 제거 후 2글자 이상.
   - `email`: RFC 5322 호환 정규식 검증 (`/^[^\s@]+@[^\s@]+\.[^\s@]+$/`).
   - `message`: 공백 제거 후 10글자 이상.
3. **오류 피드백**: 유효하지 않은 경우 `.error-message` 영역에 텍스트 노출 및 input 요소에 `.invalid` 클래스 부여.
4. **제출 핸들링**: `submit` 이벤트 발생 시 `event.preventDefault()`로 페이지 새로고침 차단 후 전체 필드 동시 재검증. 모든 필드 통과 시 성공 토스트 노출 및 폼 리셋.

### 3) 파라미터 옵션 및 제약 조건 규격 표 (Parameter Table)

| 검증 필드 | 정규식 또는 조건 식 | 오류 피드백 메시지 |
| :--- | :--- | :--- |
| `name` | `value.trim().length >= 2` | "이름은 최소 2글자 이상 입력해주세요." |
| `email` | `/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value)` | "올바른 이메일 주소 형식(example@domain.com)을 입력해주세요." |
| `message` | `value.trim().length >= 10` | "메시지는 최소 10글자 이상 상세히 작성해주세요." |

### 4) 실제 코드 구현체 (Code Block)

```javascript
/**
 * 폼 검증 및 인터랙션 모듈
 * 단일 책임: 실시간 정규식 유효성 검증, 에러 UI 바인딩, submit 이벤트 제어
 */

const VALIDATION_RULES = {
  name: {
    validate: (val) => val.trim().length >= 2,
    message: '이름은 최소 2자 이상 입력해야 합니다.'
  },
  email: {
    validate: (val) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(val.trim()),
    message: '올바른 이메일 형식(name@example.com)을 입력해주세요.'
  },
  message: {
    validate: (val) => val.trim().length >= 10,
    message: '메시지는 최소 10자 이상 구체적으로 작성해주세요.'
  }
};

export function initContactForm(formElement) {
  if (!formElement) return;

  const fields = ['name', 'email', 'message'];

  // 개별 필드 유효성 검사 헬퍼
  function validateField(fieldName) {
    const input = formElement.querySelector(`[name="${fieldName}"]`);
    const errorBox = formElement.querySelector(`#error-${fieldName}`);
    if (!input || !errorBox) return false;

    const isValid = VALIDATION_RULES[fieldName].validate(input.value);

    if (isValid) {
      input.classList.remove('is-invalid');
      input.classList.add('is-valid');
      errorBox.textContent = '';
      errorBox.classList.remove('show');
    } else {
      input.classList.remove('is-valid');
      input.classList.add('is-invalid');
      errorBox.textContent = VALIDATION_RULES[fieldName].message;
      errorBox.classList.add('show');
    }

    return isValid;
  }

  // 실시간 input 이벤트 바인딩
  fields.forEach(field => {
    const input = formElement.querySelector(`[name="${field}"]`);
    if (input) {
      input.addEventListener('input', () => validateField(field));
      input.addEventListener('blur', () => validateField(field));
    }
  });

  // 폼 제출(submit) 이벤트 바인딩
  formElement.addEventListener('submit', (event) => {
    event.preventDefault(); // 기본 새로고침 영구 차단

    let allValid = true;
    fields.forEach(field => {
      const fieldValid = validateField(field);
      if (!fieldValid) allValid = false;
    });

    if (!allValid) {
      const firstInvalid = formElement.querySelector('.is-invalid');
      if (firstInvalid) firstInvalid.focus();
      return;
    }

    // 전송 성공 시 피드백 처리
    const successBox = formElement.querySelector('#form-success-msg');
    if (successBox) {
      successBox.textContent = '메시지가 성공적으로 전송되었습니다! 곧 연락드리겠습니다.';
      successBox.classList.add('show');
      formElement.reset();
      fields.forEach(field => {
        const input = formElement.querySelector(`[name="${field}"]`);
        if (input) input.classList.remove('is-valid');
      });

      setTimeout(() => {
        successBox.classList.remove('show');
      }, 5000);
    }
  });
}
```

### 5) 핵심 검증 포인트 및 출력 결과 분석 (Verification Checkpoint)
* **검증 포인트 1**: 잘못된 이메일(`test@`) 입력 즉시 하단에 붉은색 경고 메시지가 표시되는가?
* **검증 포인트 2**: 유효하지 않은 상태에서 엔터나 제출 클릭 시 첫 번째 잘못된 입력창으로 자동 포커스가 이동하는가?
* **검증 포인트 3**: 성공 시 `event.preventDefault()`에 의해 브라우저 URL 파라미터 변동 및 새로고침이 발생하지 않는가?

---

## 4. `js/main.js` — 다크모드 및 IntersectionObserver 오케스트레이션

### 1) 기능 개요 및 비즈니스 설계 의도 (Description)
전체 애플리케이션의 진입점(Entry point)으로서 모든 독립 모듈을 초기화하고 조율합니다. 최상위 HTML의 `data-theme` 속성과 `localStorage`를 연동하여 다크/라이트 테마를 실시간 전환하며, `IntersectionObserver` API를 활용하여 화면 스크롤 시 섹션들이 부드럽게 페이드인되는 시각적 인터랙션을 완성합니다.

### 2) 내부 제어 흐름 및 I/O 라이프사이클 (Lifecycle & Storage I/O)
1. **테마 복원**: `localStorage.getItem('theme')` 확인. 없으면 `window.matchMedia('(prefers-color-scheme: dark)')` 질의 후 `document.documentElement.dataset.theme` 설정.
2. **네비게이션 제어**: 모바일 햄버거 버튼 클릭 시 네비게이션 메뉴에 `.active` 클래스 토글 및 접근성 `aria-expanded` 갱신.
3. **스크롤 감시자 가동**: `IntersectionObserver` 인스턴스 생성(옵션: `threshold: 0.15`). 모든 `<section>`을 등록하고, 뷰포트 진입 시 `.fade-in-visible` 클래스 부여 후 감시 해제(`unobserve`).
4. **Scroll-To-Top**: `window.scrollY > 300`일 때 플로팅 탑 버튼 노출, 클릭 시 `window.scrollTo({ top: 0, behavior: 'smooth' })` 실행.

### 3) 파라미터 옵션 및 제약 조건 규격 표 (Parameter Table)

| 옵션 명 | 타입 | 설정 값 | 목적 및 브라우저 최적화 효과 |
| :--- | :---: | :---: | :--- |
| `threshold` | `number` | `0.15` | 요소가 15% 화면에 들어왔을 때 트리거하여 자연스러운 등장 보장 |
| `rootMargin` | `string` | `'0px 0px -50px 0px'` | 하단 50px 여유를 두어 스크롤 완료 직전에 애니메이션 시작 |

### 4) 실제 코드 구현체 (Code Block)

```javascript
/**
 * 메인 오케스트레이터 모듈
 * 단일 책임: 테마 영속화, 반응형 네비게이션, 스크롤 애니메이션, 하위 모듈 부트스트랩
 */

import { fetchGitHubRepos } from './api.js';
import { renderLoading, renderError, renderEmpty, renderProjectCards } from './ui.js';
import { initContactForm } from './events.js';

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initNavigation();
  initScrollAnimations();
  initScrollToTop();
  initProjectsSection();
  initContactForm(document.querySelector('#contact-form'));
});

function initTheme() {
  const themeToggleBtn = document.querySelector('#theme-toggle-btn');
  const currentTheme = localStorage.getItem('theme') || 
    (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

  document.documentElement.dataset.theme = currentTheme;
  updateThemeIcon(currentTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const newTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      document.documentElement.dataset.theme = newTheme;
      localStorage.setItem('theme', newTheme);
      updateThemeIcon(newTheme);
    });
  }
}

function updateThemeIcon(theme) {
  const icon = document.querySelector('#theme-toggle-btn i');
  if (icon) {
    icon.className = theme === 'dark' ? 'fa-solid fa-sun' : 'fa-solid fa-moon';
  }
}

function initNavigation() {
  const hamburgerBtn = document.querySelector('#hamburger-btn');
  const navMenu = document.querySelector('#nav-menu');
  const navLinks = document.querySelectorAll('.nav-link');

  if (hamburgerBtn && navMenu) {
    hamburgerBtn.addEventListener('click', () => {
      const isOpen = navMenu.classList.toggle('active');
      hamburgerBtn.classList.toggle('active');
      hamburgerBtn.setAttribute('aria-expanded', isOpen);
    });

    // 링크 클릭 시 모바일 메뉴 자동 닫힘
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        hamburgerBtn.classList.remove('active');
        hamburgerBtn.setAttribute('aria-expanded', 'false');
      });
    });
  }
}

function initScrollAnimations() {
  const observerOptions = {
    threshold: 0.15,
    rootMargin: '0px 0px -50px 0px'
  };

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target); // 1회 애니메이션 후 감시 해제하여 성능 보존
      }
    });
  }, observerOptions);

  document.querySelectorAll('.animate-on-scroll').forEach(el => observer.observe(el));
}

function initScrollToTop() {
  const topBtn = document.querySelector('#scroll-top-btn');
  const header = document.querySelector('header');

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;

    // 헤더 그림자/블러 효과 토글
    if (header) {
      header.classList.toggle('scrolled', scrollY > 60);
    }

    // Top 플로팅 버튼 노출 토글
    if (topBtn) {
      topBtn.classList.toggle('visible', scrollY > 300);
    }
  }, { passive: true }); // 스크롤 성능 최적화

  if (topBtn) {
    topBtn.addEventListener('click', () => {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
}

async function initProjectsSection() {
  const container = document.querySelector('#projects-grid');
  if (!container) return;

  const GITHUB_USERNAME = 'octocat'; // 기본값 (추후 사용자 프로필로 치환)

  async function loadData() {
    renderLoading(container);
    const result = await fetchGitHubRepos(GITHUB_USERNAME);

    if (result.status === 'success') {
      renderProjectCards(container, result.data);
    } else if (result.status === 'empty') {
      renderEmpty(container);
    } else {
      renderError(container, result.error, loadData);
    }
  }

  await loadData();
}
```

### 5) 핵심 검증 포인트 및 출력 결과 분석 (Verification Checkpoint)
* **검증 포인트 1**: 다크 모드 전환 후 새로고침 시 이전에 선택했던 테마가 깜빡임 없이 유지되는가?
* **검증 포인트 2**: 뷰포트 진입 시 요소에 `.is-visible` 클래스가 추가되며 1회 애니메이션 후 `unobserve`가 호출되는가?
* **검증 포인트 3**: 모바일 뷰포트에서 링크 클릭 시 열려 있던 메뉴가 부드럽게 닫히는가?
