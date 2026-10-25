/**
 * 메인 엔트리포인트 및 오케스트레이터 모듈
 * 단일 책임: 전역 상태 초기화, 테마 관리, 반응형 네비게이션, 스크롤 애니메이션, 하위 모듈 부트스트랩
 */

import { fetchGitHubRepos, MOCK_FALLBACK_REPOS, API_STATUS } from './api.js';
import { renderLoading, renderError, renderEmpty, renderProjectCards } from './ui.js';
import { initContactForm } from './events.js';

// 기본 연동 대상 GitHub 계정 (실제 사용자 GitHub 계정)
const DEFAULT_GITHUB_USER = 'newcode99';

document.addEventListener('DOMContentLoaded', () => {
  initThemeManager();
  initNavigationManager();
  initScrollEffects();
  initIntersectionObserver();
  initProjectsSection();
  initContactForm(document.querySelector('#contact-form'));
});

/**
 * 다크/라이트 모드 테마 관리자
 */
function initThemeManager() {
  const themeToggleBtn = document.querySelector('#theme-toggle-btn');
  const savedTheme = localStorage.getItem('theme');
  const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  const currentTheme = savedTheme || (prefersDark ? 'dark' : 'light');

  // DOM 속성 및 아이콘 동기화
  applyTheme(currentTheme);

  if (themeToggleBtn) {
    themeToggleBtn.addEventListener('click', () => {
      const activeTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
      applyTheme(activeTheme);
      localStorage.setItem('theme', activeTheme);
    });
  }

  // OS 시스템 테마 변경 실시간 감지 (사용자가 수동 변경하지 않은 경우)
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!localStorage.getItem('theme')) {
      applyTheme(e.matches ? 'dark' : 'light');
    }
  });
}

function applyTheme(theme) {
  document.documentElement.dataset.theme = theme;
  const themeIcon = document.querySelector('#theme-toggle-btn i');
  if (themeIcon) {
    if (theme === 'dark') {
      themeIcon.className = 'fa-solid fa-sun';
      themeIcon.parentElement.setAttribute('title', '라이트 모드로 전환');
    } else {
      themeIcon.className = 'fa-solid fa-moon';
      themeIcon.parentElement.setAttribute('title', '다크 모드로 전환');
    }
  }
}

/**
 * 반응형 네비게이션 및 모바일 햄버거 메뉴 관리자
 */
function initNavigationManager() {
  const hamburgerBtn = document.querySelector('#hamburger-btn');
  const navMenu = document.querySelector('#nav-menu');
  const navLinks = document.querySelectorAll('.nav-link');

  if (hamburgerBtn && navMenu) {
    // 햄버거 버튼 토글
    hamburgerBtn.addEventListener('click', () => {
      const isOpen = navMenu.classList.toggle('active');
      hamburgerBtn.classList.toggle('active');
      hamburgerBtn.setAttribute('aria-expanded', String(isOpen));
    });

    // 네비게이션 링크 클릭 시 모바일 메뉴 자동 닫힘
    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        navMenu.classList.remove('active');
        hamburgerBtn.classList.remove('active');
        hamburgerBtn.setAttribute('aria-expanded', 'false');
      });
    });

    // 외부 영역 클릭 시 모바일 메뉴 닫기
    document.addEventListener('click', (event) => {
      if (!navMenu.contains(event.target) && !hamburgerBtn.contains(event.target)) {
        navMenu.classList.remove('active');
        hamburgerBtn.classList.remove('active');
        hamburgerBtn.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // 스크롤 위치에 따른 활성 네비게이션 링크 하이라이트 (Scrollspy)
  const sections = document.querySelectorAll('section[id]');
  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;

    sections.forEach(section => {
      const sectionHeight = section.offsetHeight;
      const sectionTop = section.offsetTop - 120;
      const sectionId = section.getAttribute('id');

      if (scrollY >= sectionTop && scrollY < sectionTop + sectionHeight) {
        navLinks.forEach(link => {
          link.classList.toggle('active', link.getAttribute('href') === `#${sectionId}`);
        });
      }
    });
  }, { passive: true });
}

/**
 * 스크롤 헤더 효과 및 플로팅 Top 버튼 관리자
 */
function initScrollEffects() {
  const header = document.querySelector('#header');
  const scrollTopBtn = document.querySelector('#scroll-top-btn');

  window.addEventListener('scroll', () => {
    const scrollY = window.scrollY;

    // 60px 이상 스크롤 시 헤더 블러 및 그림자 효과
    if (header) {
      header.classList.toggle('scrolled', scrollY > 60);
    }

    // 300px 이상 스크롤 시 맨 위로 버튼 표시
    if (scrollTopBtn) {
      scrollTopBtn.classList.toggle('visible', scrollY > 300);
    }
  }, { passive: true });

  if (scrollTopBtn) {
    scrollTopBtn.addEventListener('click', () => {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });
  }
}

/**
 * 뷰포트 진입 감지 스크롤 애니메이션 (IntersectionObserver)
 */
function initIntersectionObserver() {
  const animatedElements = document.querySelectorAll('.animate-on-scroll');

  const observerOptions = {
    root: null,
    threshold: 0.12,
    rootMargin: '0px 0px -40px 0px'
  };

  const observer = new IntersectionObserver((entries, obs) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target); // 1회 애니메이션 완료 후 감시 해제 (성능 최적화)
      }
    });
  }, observerOptions);

  animatedElements.forEach(el => observer.observe(el));
}

/**
 * GitHub API 연동 및 Projects 섹션 초기화 (상태 제어기 시뮬레이터 포함)
 */
async function initProjectsSection() {
  const container = document.querySelector('#projects-container');
  const stateBtns = document.querySelectorAll('.state-btn');
  if (!container) return;

  let cachedRepos = null;

  function updateActiveButton(state) {
    stateBtns.forEach(btn => {
      const isMatch = btn.getAttribute('data-state') === state;
      btn.classList.toggle('active', isMatch);
      btn.setAttribute('aria-selected', String(isMatch));
    });
  }

  async function applyState(state, forceReload = false) {
    updateActiveButton(state);

    switch (state) {
      case 'loading':
        renderLoading(container);
        break;

      case 'empty':
        renderEmpty(container);
        break;

      case 'error':
        renderError(
          container,
          'GitHub API 호출 한도 초과(403 Rate Limit) 또는 일시적 네트워크 장애가 감지되었습니다. (상태 검증 시뮬레이션)',
          () => applyState('success', true),
          () => {
            renderProjectCards(container, MOCK_FALLBACK_REPOS);
            updateActiveButton('success');
          }
        );
        break;

      case 'success':
      default:
        if (cachedRepos && !forceReload) {
          renderProjectCards(container, cachedRepos);
        } else {
          renderLoading(container);
          const result = await fetchGitHubRepos(DEFAULT_GITHUB_USER, 6);
          if (result.status === API_STATUS.SUCCESS) {
            cachedRepos = result.data;
            renderProjectCards(container, result.data);
          } else if (result.status === API_STATUS.EMPTY) {
            renderEmpty(container);
            updateActiveButton('empty');
          } else {
            renderError(
              container,
              result.error || '프로젝트를 불러오지 못했습니다.',
              () => applyState('success', true),
              () => {
                renderProjectCards(container, MOCK_FALLBACK_REPOS);
                updateActiveButton('success');
              }
            );
            updateActiveButton('error');
          }
        }
        break;
    }
  }

  // 상태 전환 버튼 클릭 리스너 연결 (순수 addEventListener)
  stateBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetState = btn.getAttribute('data-state');
      if (targetState) {
        applyState(targetState);
      }
    });
  });

  // 콘솔 및 외부 제어용 전역 API 등록
  window.setProjectsState = (state) => {
    applyState(state);
  };

  // 초기 로드 실행
  await applyState('success');
}

