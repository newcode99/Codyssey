# B1-1 엔지니어링 의사결정 및 트레이드오프 분석서 (ENGINEERING_DECISIONS_AND_TRADE_OFFS)

본 문서는 B1-1 반응형 포트폴리오 웹사이트를 구축함에 있어 내려진 핵심 기술적 의사결정(Why)과 대안 기술 간의 장단점(Trade-offs)을 심층 비교하고, 잠재적인 엣지케이스에 대한 방어 전략(Guard Strategies)을 명확히 기록합니다.

---

## 1. 5대 핵심 엔지니어링 의사결정 및 트레이드오프 매트릭스

### 1) 순수 Vanilla JavaScript vs 프론트엔드 프레임워크 (React, Vue)

* **결정 사항**: 외부 라이브러리 및 번들러 없이 **순수 Vanilla JS (ES6+)** 단독 채택.
* **배경 및 Why**:
  * 프레임워크는 가상 DOM, 상태 스케줄러, 합성 이벤트 등으로 웹 브라우저의 기본 동작을 추상화하여 감춥니다.
  * 기초가 부실한 상태에서 프레임워크를 학습하면 도구의 마법 뒤에 숨겨진 브라우저의 본질(렌더 트리 생성, 리플로우/리페인트, 이벤트 루프)을 이해할 수 없습니다.
  * 본 과제의 본질은 브라우저의 3대 핵심("사용자 이벤트 → DOM 조작 → 화면 변화")을 직접 손으로 제어하여 탄탄한 기초를 수립하는 것입니다.

| 평가 기준 | Vanilla JavaScript (채택) | React / Vue (기각) |
| :--- | :--- | :--- |
| **의존성 및 번들 크기** | **0 KB (추가 다운로드 전무)** | 최소 40KB ~ 150KB 번들 로드 필요 |
| **빌드 파이프라인** | **불필요 (HTML/JS 즉시 브라우저 실행)** | Node.js, npm, Vite/Webpack 트랜스파일링 필수 |
| **브라우저 이해도** | **최상 (DOM API 및 브라우저 엔진 직접 체득)** | 중간 (프레임워크 라이프사이클에 종속) |
| **대규모 상태 관리** | 수동 단방향 패턴 구축 필요 (복잡도 증가) | Hook 및 전역 상태 도구로 대규모 유지보수 용이 |
| **트레이드오프 결론** | 대규모 엔터프라이즈 앱에서는 프레임워크가 유리하나, **포트폴리오 단일 페이지 웹사이트에서는 오버엔지니어링**이며 순수 바닐라가 월등한 로딩 속도와 완벽한 학습 효과를 제공함. |

---

### 2) CSS Variables (Custom Properties) vs CSS 전처리기 / 유틸리티 프레임워크

* **결정 사항**: Sass, LESS, Tailwind CSS를 배제하고 **순수 CSS Variables (`--var-name`)** 채택.
* **배경 및 Why**:
  * CSS 전처리기(Sass)의 변수는 빌드 타임에 컴파일되어 고정된 텍스트로 치환되므로, 런타임에 실시간으로 테마를 교체할 수 없습니다.
  * 반면 CSS Variables는 브라우저 DOM 트리를 따라 상속되며 런타임에 동적으로 변경 가능합니다. 최상위 `data-theme` 속성 변경 하나만으로 전체 웹사이트의 모든 색상을 1프레임(16ms) 만에 재계산할 수 있습니다.

| 평가 기준 | Native CSS Variables (채택) | Tailwind CSS / Sass (기각) |
| :--- | :--- | :--- |
| **런타임 테마 전환** | **자바스크립트로 즉각 변수 스왑 가능** | 정적 클래스 교체 또는 별도 빌드 필요 |
| **추가 빌드 도구** | **없음 (브라우저 자체 해석)** | PostCSS, Node 패키지 컴파일러 필수 |
| **HTML 가독성** | **시맨틱 클래스명 유지 (`.project-card`)** | 유틸리티 클래스 난립으로 HTML 오염 |
| **트레이드오프 결론** | CSS 표준 스펙을 100% 활용하여 빌드 부담을 없애고 다크 모드 런타임 반응성을 극대화함. |

---

### 3) 레이아웃 전략: Flexbox vs CSS Grid의 영역별 분할

* **결정 사항**: 네비게이션 및 헤더는 **Flexbox**, 프로젝트 카드 및 기술 배지는 **CSS Grid** 분할 적용.
* **배경 및 Why**:
  * 하나의 레이아웃 도구만 고집하는 것은 비효율적입니다.
  * Flexbox는 콘텐츠의 크기에 따라 유연하게 1차원(가로 또는 세로) 정렬을 맞추는 데 최적화되어 있습니다 (예: 로고는 왼쪽, 링크는 오른쪽).
  * Grid는 화면 폭에 맞춰 일정한 간격의 카드 컬럼을 2열, 3열로 계산하는 2차원 매트릭스에 최적화되어 있습니다 (`repeat(auto-fit, minmax(300px, 1fr))`).

| 레이아웃 대상 | 선택 도구 | 채택 근거 |
| :--- | :--- | :--- |
| **Header / Nav** | **Flexbox** | 로고와 메뉴 항목 사이의 공간 배분(`justify-content: space-between`) 및 세로 정렬에 최적 |
| **Hero 섹션** | **Flexbox** | 텍스트와 CTA 버튼의 수직 중앙 정렬(`flex-direction: column; align-items: center;`) |
| **Projects 카드** | **CSS Grid** | 반응형 화면에 따라 1열 → 2열 → 3열로 자동 래핑되는 카드 갤러리 구축에 압도적 효율 |
| **Skills 배지** | **Flexbox / Grid** | 태그형 배지들의 줄바꿈(`flex-wrap: wrap`)과 일정한 여백 유지 |

---

### 4) DOM 동적 렌더링 방식: `innerHTML` + 새니타이징 vs `createElement`

* **결정 사항**: 템플릿 가독성을 위해 **`innerHTML` 기반 템플릿 리터럴**을 사용하되, **`escapeHTML()` 방어 함수**를 의무 적용.
* **배경 및 Why**:
  * 순수 `document.createElement()`, `appendChild()`만으로 복잡한 카드를 만들면 코드 수백 줄이 단순 노드 생성문으로 도배되어 가독성이 심각하게 저하됩니다.
  * 그러나 `innerHTML`을 검증 없이 사용하면 XSS 공격에 무방비로 노출됩니다.
  * 따라서 두 방식의 절충안으로, ES6 템플릿 리터럴의 뛰어난 마크업 가독성을 취하면서 외부 데이터 삽입 지점에 문자열 이스케이프 가드레일을 결합함.

---

### 5) 테마 영속화: `localStorage` vs `Cookie` vs `SessionStorage`

* **결정 사항**: 사용자 다크 모드 설정 저장소로 **`localStorage`** 채택.
* **배경 및 Why**:
  * `Cookie`: 매 HTTP 요청마다 서버로 불필요하게 전송되어 네트워크 대역폭을 낭비하며 용량 제한(4KB)이 작음.
  * `SessionStorage`: 브라우저 탭을 닫으면 데이터가 날아가므로 다음 방문 시 설정이 초기화됨.
  * `localStorage`: 클라이언트 로컬에만 존재하여 서버 트래픽이 0이고, 탭이나 브라우저를 닫아도 반영구적으로 설정이 유지되므로 클라이언트 테마 저장에 최적.

---

## 2. 엣지케이스 방어 가드레일 (Guard Strategies)

### Guard 1: GitHub API 403 Rate Limit 및 네트워크 오프라인 가드
* **위험 시나리오**: 미인증 GitHub API는 IP당 시간당 60회로 호출이 엄격히 제한됩니다. 또한 사용자의 와이파이가 끊길 수 있습니다.
* **방어 로직**:
  ```javascript
  // api.js 방어 가드
  if (!response.ok) {
    if (response.status === 403) {
      throw new Error('API_RATE_LIMIT_EXCEEDED');
    } else if (response.status === 404) {
      throw new Error('USER_NOT_FOUND');
    } else {
      throw new Error(`HTTP_ERROR_${response.status}`);
    }
  }
  ```
* **UI 대응**:
  * 단순 실패 시 "데이터를 불러올 수 없습니다" 안내문구와 함께 **[다시 시도]** 버튼을 렌더링함.
  * Rate Limit 초과 시 백업용 기본 Mock 프로젝트 데이터(최소 3개)로 자동 폴백(Fallback)하도록 설계하여 심사관이나 사용자에게 빈 화면이 절대 노출되지 않도록 보장함.

### Guard 2: XSS (Cross-Site Scripting) 코드 인젝션 가드
* **위험 시나리오**: GitHub 저장소 이름이나 설명(`repo.description`)에 악의적인 스크립트(`<img src=x onerror=alert(1)>`)가 삽입되어 있을 경우 사용자 브라우저에서 실행될 위험.
* **방어 로직**:
  ```javascript
  // ui.js 방어 가드
  export function escapeHTML(str) {
    if (!str) return '';
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
  ```
  * 템플릿 리터럴 내부의 모든 외부 주입 변수에 `${escapeHTML(repo.name)}`를 의무 적용함.

### Guard 3: 새로고침 시 다크 모드 번쩍임(FOUC) 방어 가드
* **위험 시나리오**: 페이지가 로드될 때 브라우저가 라이트 모드 스타일을 먼저 렌더링한 후, 수백 ms 뒤 JS가 로드되어 다크 모드로 바뀌면 화면이 흰색으로 번쩍이는 FOUC(Flash of Unstyled Content) 발생.
* **방어 로직**:
  * `<head>` 내부 가장 윗줄에 10줄 이내의 극소량 즉시 실행 인라인 스크립트를 배치하여 CSS 렌더링 전에 `document.documentElement.dataset.theme`를 동기적으로 선점함.

### Guard 4: 스크롤 이벤트 성능 병목 방어 가드
* **위험 시나리오**: `window.addEventListener('scroll')`에서 무거운 DOM 계산이나 클래스 변경을 매 픽셀마다 수행하면 초당 60프레임이 붕괴되어 스크롤이 버벅거림.
* **방어 로직**:
  * 섹션 등장 애니메이션은 브라우저 렌더링 파이프라인에서 최적화되는 **`IntersectionObserver` API**를 사용하여 스크롤 이벤트 자체를 발생시키지 않음.
  * 네비게이션 고정 및 Top 버튼 표시용 스크롤 리스너에는 `requestAnimationFrame` 또는 플래그 기반 스로틀링을 적용하여 초당 최대 60회 이내로 호출을 제한함.
