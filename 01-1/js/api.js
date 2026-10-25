/**
 * GitHub API 통신 및 데이터 정제 모듈
 * 단일 책임: GitHub REST API 비동기 요청, 4대 상태 머신 제어, 오류 캡슐화
 */

export const API_STATUS = {
  IDLE: 'idle',
  LOADING: 'loading',
  SUCCESS: 'success',
  ERROR: 'error',
  EMPTY: 'empty'
};

// Rate Limit(시간당 60회 초과) 또는 오프라인 대비용 견고한 데모 프로젝트 데이터
export const MOCK_FALLBACK_REPOS = [
  {
    id: 101,
    name: 'vanilla-spa-framework',
    description: '외부 의존성 없이 순수 Vanilla JS로 구축한 가상 라우터 및 단방향 상태 관리 엔진',
    language: 'JavaScript',
    stars: 128,
    forks: 34,
    url: 'https://github.com',
    updatedAt: '2026. 10. 20.'
  },
  {
    id: 102,
    name: 'glassmorphism-design-tokens',
    description: 'CSS Variables와 반응형 Grid를 결합한 현대적 글래스모피즘 웹 UI 토큰 라이브러리',
    language: 'CSS',
    stars: 95,
    forks: 18,
    url: 'https://github.com',
    updatedAt: '2026. 10. 18.'
  },
  {
    id: 103,
    name: 'a11y-web-standards-audit',
    description: '웹 접근성(WCAG 2.1) 준수 및 시맨틱 HTML 자동 무결성 검증 도구',
    language: 'HTML',
    stars: 76,
    forks: 12,
    url: 'https://github.com',
    updatedAt: '2026. 10. 15.'
  },
  {
    id: 104,
    name: 'async-state-machine-handler',
    description: 'Fetch API와 Promise를 활용한 실시간 통신 및 4-State UI 상태 제어 아키텍처',
    language: 'JavaScript',
    stars: 114,
    forks: 29,
    url: 'https://github.com',
    updatedAt: '2026. 10. 11.'
  },
  {
    id: 105,
    name: 'responsive-portfolio-kit',
    description: '모바일 퍼스트 원칙에 기반한 현대적인 프론트엔드 포트폴리오 템플릿',
    language: 'JavaScript',
    stars: 204,
    forks: 51,
    url: 'https://github.com',
    updatedAt: '2026. 10. 05.'
  },
  {
    id: 106,
    name: 'performance-intersection-observer',
    description: '스크롤 렌더링 성능 최적화를 위한 뷰포트 진입 감지 및 가상 스크롤 모듈',
    language: 'TypeScript',
    stars: 88,
    forks: 16,
    url: 'https://github.com',
    updatedAt: '2026. 09. 28.'
  }
];

/**
 * GitHub 사용자 공개 저장소 비동기 수집 함수
 * @param {string} username - GitHub 계정 ID
 * @param {number} perPage - 표시할 최대 저장소 수 (기본: 6)
 * @returns {Promise<{ status: string, data: Array, error?: string }>}
 */
export async function fetchGitHubRepos(username = '', perPage = 6) {
  if (!username || typeof username !== 'string') {
    return {
      status: API_STATUS.ERROR,
      error: '유효한 GitHub 사용자 이름을 지정해야 합니다.',
      data: []
    };
  }

  const endpoint = `https://api.github.com/users/${encodeURIComponent(username)}/repos?sort=updated&per_page=30`;

  try {
    const response = await fetch(endpoint, {
      headers: {
        'Accept': 'application/vnd.github.v3+json'
      }
    });

    // 1. HTTP 응답 코드 가드레일 판별
    if (!response.ok) {
      if (response.status === 403) {
        throw new Error('API 호출 한도(시간당 60회)가 초과되었습니다.');
      } else if (response.status === 404) {
        throw new Error(`사용자 '${username}'을(를) 찾을 수 없습니다.`);
      } else {
        throw new Error(`GitHub 서버 응답 오류 (상태코드: ${response.status})`);
      }
    }

    const rawData = await response.json();

    // 2. Fork 저장소 배제 및 최신 업데이트 순 정렬 상위 N개 추출
    const filteredRepos = rawData
      .filter(repo => !repo.fork)
      .slice(0, perPage)
      .map(repo => ({
        id: repo.id,
        name: repo.name,
        description: repo.description || '상세 프로젝트 설명이 등록되지 않은 저장소입니다.',
        language: repo.language || 'Plain Text',
        stars: repo.stargazers_count,
        forks: repo.forks_count,
        url: repo.html_url,
        updatedAt: new Date(repo.updated_at).toLocaleDateString('ko-KR')
      }));

    // 3. 빈 저장소(Empty state) 처리
    if (filteredRepos.length === 0) {
      return {
        status: API_STATUS.EMPTY,
        data: []
      };
    }

    // 4. 성공(Success state) 반환
    return {
      status: API_STATUS.SUCCESS,
      data: filteredRepos
    };

  } catch (error) {
    // 5. 에러(Error state) 캡슐화 반환
    return {
      status: API_STATUS.ERROR,
      error: error.message || '네트워크 연결 상태를 확인해주세요.',
      data: []
    };
  }
}
