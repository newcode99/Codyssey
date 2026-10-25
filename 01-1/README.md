# B1-1 반응형 포트폴리오 웹사이트 (Responsive Developer Portfolio)

> **외부 프레임워크와 라이브러리 없이 순수 HTML5, CSS3, Vanilla JavaScript(ES6+)만으로 완성한 모던 반응형 포트폴리오 웹사이트**

---

## 1. 프로젝트 개요 및 미션 의도

HTML, CSS, JavaScript는 모든 웹 프론트엔드 기술의 기초이자 브라우저가 직접 해석하는 유일한 언어입니다. React, Vue, Angular 같은 현대 프레임워크 역시 결국 이 세 가지 표준 기술로 트랜스파일되어 브라우저에서 동작합니다.

본 프로젝트는 무거운 외부 라이브러리나 번들러 없이, **"사용자 이벤트 → 상태 머신 전이 → 최적화된 DOM 렌더링"** 으로 이어지는 웹 브라우저의 핵심 동작 메커니즘을 순수 바닐라 기술로 실증 구현하였습니다.

---

## 2. 핵심 기술 스택 및 아키텍처 원칙

### 1) 기술 스택 (Zero Dependency)
* **Core Markup**: HTML5 Semantic Elements (`header`, `nav`, `main`, `section`, `article`, `footer`)
* **Styling**: Pure Modern CSS3 (CSS Variables, Flexbox, CSS Grid, Mobile-First Media Queries)
* **Logic**: Vanilla JavaScript ES6+ (Native ES Modules, Fetch API, Async/Await, IntersectionObserver)
* **Icons & Fonts**: Font Awesome 6.5.1 (CDN), Google Fonts (Inter & Outfit)
* **외부 프레임워크 사용**: **0% (Zero React, Zero Tailwind, Zero jQuery)**

### 2) 모듈 책임 분리 (SRP Architecture)
```
B1-1/
├── index.html           # 6대 섹션 시맨틱 마크업, a11y, Zero-FOUC 테마 선행 스크립트
├── css/
│   └── style.css        # CSS 변수 토큰, 다크모드, 반응형 레이아웃, 마이크로 애니메이션
├── js/
│   ├── main.js          # 전역 초기화, 테마 관리, 햄버거 토글, IntersectionObserver 스크롤
│   ├── api.js           # GitHub REST API 비동기 페칭, 4대 상태 머신, 가드레일
│   ├── ui.js            # 순수 DOM 렌더링, XSS 방어 새니타이저(escapeHTML), 상태별 UI
│   └── events.js        # 정규식 폼 실시간 유효성 검사, preventDefault 캡슐화
├── images/              # 고해상도 개발자 프로필 및 3D 테크 그래픽 자산
├── atifact/             # 사전 엔지니어링 설계 및 학습 아티팩트 6종 (01~06.md)
├── web_evaluation/      # 브라우저 기반 인터랙티브 기술 평가 대시보드
├── TASK_SPECIFICATION.md# 과제 요구사항 전수 명세서
└── STEP_BY_STEP_EXECUTION_AND_TEST_GUIDE.md # 챕터별 공식 실행 및 테스트 가이드
```

---

## 3. 핵심 구현 기능 하이라이트

### 1) 밝고 화사한 프리미엄 글래스모피즘 디자인 (Light Mode Default)
* 화사한 퓨어 화이트 & 소프트 크림 배경(`--bg-primary: #f8fafc;`)과 세련된 인디고/바이올렛 액센트(`--primary: #4f46e5;`)를 결합.
* 투명도와 블러 효과를 살린 글래스모피즘(`backdrop-filter: blur(12px)`) 네비게이션 및 카드 디자인.

### 2) 무깜빡임(Zero-FOUC) 다크 모드 테마 스위처
* `<head>` 상단 인라인 동기 스크립트로 새로고침 시 화면이 하얗게 튀는 FOUC 현상을 원천 방어.
* `localStorage`와 브라우저 `prefers-color-scheme`을 연동한 영구 테마 보존.

### 3) GitHub REST API 4대 상태 머신 (4-State Machine)
* `Loading` (스피너 애니메이션) $\rightarrow$ `Success` (정제된 6개 카드 렌더링) $\rightarrow$ `Error` (403 한도초과 대응 에러문 + 재시도 버튼) $\rightarrow$ `Empty` (빈 저장소 안내).
* Fork 저장소 제외 필터링 및 최신 업데이트 순 정렬.
* 시간당 60회 Rate Limit 초과 시에도 정상 시연이 가능한 데모 프로젝트 Fallback 모드 완비.

### 4) 실시간 정규식 Contact 폼 밸리데이션
* 이름 2자 이상, RFC 5322 이메일 규격, 메시지 10자 이상 실시간 검증.
* `event.preventDefault()`로 브라우저 새로고침을 완벽 차단하고 친절한 녹색 토스트 알림 렌더링.

### 5) 모바일 퍼스트 반응형 및 웹 접근성 (a11y)
* 375px 모바일 뷰포트 완벽 지원 및 'X' 자로 변형되는 햄버거 드로어 메뉴.
* 모든 폼 컨트롤 `label for="id"` 100% 매핑, 모든 이미지 `alt` 속성 부여.

---

## 4. 로컬 실행 및 브라우저 테스트 방법

ES6 모듈을 올바르게 구동하기 위해 표준 HTTP 웹서버를 실행합니다.

```bash
# 1. B1-1 디렉토리로 이동
cd /Users/hwangjeonghyeon/codyssey_2026/2-1/B1-1

# 2. 내장 HTTP 웹서버 기동
python3 -m http.server 8088

# 3. 브라우저 접속
# 메인 포트폴리오 웹사이트: http://localhost:8088/
# 기술 평가 마스터 대시보드: http://localhost:8088/web_evaluation/index.html
```

---

## 5. 브라우저 실증 검증 완료 내역

| 검증 시나리오 | 검증 내역 | 판정 |
| :--- | :--- | :---: |
| **전체 6대 섹션 렌더링** | Hero, About, Skills, Projects, Contact, Footer UI 정상 | ✅ PASS |
| **브라우저 콘솔 로그** | JavaScript 런타임 에러 0건, 네트워크 실패 0건 | ✅ PASS |
| **다크/라이트 테마 전환** | `#theme-toggle-btn` 클릭 시 즉시 스왑 및 새로고침 유지 | ✅ PASS |
| **GitHub API 실시간 연동** | 최신 6개 공개 저장소 카드 그리드 동적 렌더링 | ✅ PASS |
| **Contact 폼 실시간 검증** | 빈값 에러, 정규식 검증, 성공 피드백 정상 출력 | ✅ PASS |
| **모바일 반응형 햄버거** | 375px 뷰포트에서 드로어 메뉴 열림/닫힘 정상 작동 | ✅ PASS |

---

## 6. GitHub Pages 배포 가이드

1. GitHub 저장소의 `Settings` > `Pages` 메뉴로 이동합니다.
2. `Source` 항목에서 `Deploy from a branch`를 선택합니다.
3. `Branch`를 `main` (또는 `master`) 브랜치로 지정하고 `/root` 폴더로 저장합니다.
4. 수 분 후 발행되는 배포 URL(예: `https://[username].github.io/[repo]/`)에 접속하여 외부 네트워크에서 정상 동작을 실증합니다.
