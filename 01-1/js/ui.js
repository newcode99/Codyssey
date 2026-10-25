/**
 * UI 렌더링 및 뷰 레이어 전담 모듈
 * 단일 책임: 순수 DOM 조작, XSS 새니타이징, 4대 API 상태별 화면 업데이트
 */

/**
 * XSS 공격을 방어하기 위한 문자열 이스케이프 헬퍼 함수
 * @param {string} str - 원본 문자열
 * @returns {string} - HTML 특수문자가 엔티티로 치환된 안전한 문자열
 */
export function escapeHTML(str) {
  if (str === null || str === undefined) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * 로딩 상태 UI 렌더링
 * @param {HTMLElement} container - 렌더링 타겟 컨테이너
 */
export function renderLoading(container) {
  if (!container) return;
  container.innerHTML = `
    <div class="status-box loading-box" role="status" aria-live="polite">
      <div class="spinner" aria-hidden="true"></div>
      <p>GitHub 최신 프로젝트를 불러오는 중입니다...</p>
    </div>
  `;
}

/**
 * 에러 상태 UI 렌더링 (재시도 및 데모 모드 버튼 제공)
 * @param {HTMLElement} container - 렌더링 타겟 컨테이너
 * @param {string} errorMessage - 에러 메시지
 * @param {Function} onRetry - 재시도 콜백 핸들러
 * @param {Function} onUseMock - 데모 프로젝트 불러오기 콜백
 */
export function renderError(container, errorMessage, onRetry, onUseMock) {
  if (!container) return;
  container.innerHTML = `
    <div class="status-box error-box" role="alert">
      <i class="fa-solid fa-triangle-exclamation status-icon" aria-hidden="true"></i>
      <p class="error-msg"><strong>프로젝트를 불러오지 못했습니다.</strong><br>${escapeHTML(errorMessage)}</p>
      <div class="error-actions">
        <button class="btn btn-primary" id="retry-fetch-btn">
          <i class="fa-solid fa-rotate-right"></i> 다시 시도
        </button>
        <button class="btn btn-secondary" id="demo-mode-btn">
          <i class="fa-solid fa-eye"></i> 데모 프로젝트 확인
        </button>
      </div>
    </div>
  `;

  const retryBtn = container.querySelector('#retry-fetch-btn');
  if (retryBtn && typeof onRetry === 'function') {
    retryBtn.addEventListener('click', onRetry);
  }

  const demoBtn = container.querySelector('#demo-mode-btn');
  if (demoBtn && typeof onUseMock === 'function') {
    demoBtn.addEventListener('click', onUseMock);
  }
}

/**
 * 빈 상태 UI 렌더링 (저장소가 없을 때)
 * @param {HTMLElement} container - 렌더링 타겟 컨테이너
 */
export function renderEmpty(container) {
  if (!container) return;
  container.innerHTML = `
    <div class="status-box empty-box">
      <i class="fa-solid fa-folder-open status-icon" aria-hidden="true"></i>
      <p>등록된 공개 프로젝트가 없습니다.<br>새로운 저장소가 추가되면 실시간으로 표시됩니다.</p>
    </div>
  `;
}

/**
 * 프로젝트 카드 그리드 렌더링 (성공 상태)
 * @param {HTMLElement} container - 렌더링 타겟 컨테이너
 * @param {Array} repos - 정제된 프로젝트 배열
 */
export function renderProjectCards(container, repos) {
  if (!container || !Array.isArray(repos)) return;

  const cardsMarkup = repos.map(repo => {
    const safeName = escapeHTML(repo.name);
    const safeDesc = escapeHTML(repo.description);
    const safeLang = escapeHTML(repo.language);
    const safeUrl = escapeHTML(repo.url);

    return `
      <article class="project-card" data-id="${repo.id}">
        <div class="card-header">
          <i class="fa-regular fa-folder-closed folder-icon" aria-hidden="true"></i>
          <div class="card-links">
            <a href="${safeUrl}" target="_blank" rel="noopener noreferrer" 
               aria-label="${safeName} GitHub 저장소 바로가기 (새 창 열림)"
               title="저장소 열기">
              <i class="fa-solid fa-arrow-up-right-from-square"></i>
            </a>
          </div>
        </div>

        <h3 class="card-title">${safeName}</h3>
        <p class="card-desc">${safeDesc}</p>

        <div class="card-footer">
          <span class="card-lang">
            <span class="lang-dot"></span>${safeLang}
          </span>
          <div class="card-stats">
            <span title="Stars"><i class="fa-regular fa-star" aria-hidden="true"></i> ${repo.stars}</span>
            <span title="Forks"><i class="fa-solid fa-code-fork" aria-hidden="true"></i> ${repo.forks}</span>
          </div>
        </div>
      </article>
    `;
  }).join('');

  container.innerHTML = `
    <div class="projects-grid">
      ${cardsMarkup}
    </div>
  `;
}
