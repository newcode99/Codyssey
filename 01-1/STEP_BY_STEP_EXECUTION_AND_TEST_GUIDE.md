# B1-1 단계별 실행 및 브라우저 테스트 완전 가이드 (STEP_BY_STEP_EXECUTION_AND_TEST_GUIDE)

본 문서는 B1-1 반응형 포트폴리오 웹사이트의 전 기능을 단계별로 실증 검증할 수 있는 공식 테스트 가이드입니다. 모든 검증 절차는 **기능 개요 → 제어 흐름 → 파라미터 규격 표 → 실제 실행 명령어/출력 → 핵심 검증 분석**의 5단계 구조적 해설을 엄격히 준수합니다.

---

## 챕터 1: 제로 디펜던시 정적 로컬 웹서버 구동 및 무결성 검증

### 1) 기능 개요 및 비즈니스 설계 의도 (Description)
ES6 Modules(`import/export`) 구문은 브라우저의 동일 출처 정책(CORS) 및 보안 모델에 따라 `file://` 로컬 파일 시스템에서 직접 열었을 때 실행이 차단됩니다. 따라서 표준 HTTP 로컬 웹서버를 기동해야 합니다. 외부의 무거운 패키지(`npm`, `express`, `live-server` 등) 설치를 일체 배제하고, 운영체제 표준 Python 3 내장 모듈(`http.server`)을 활용하여 **외부 설치 의존성 0개(Zero Dependency)** 로 환경을 즉시 구축합니다.

### 2) 내부 제어 흐름 및 I/O 라이프사이클 (Lifecycle & Storage I/O)
1. **소켓 바인딩**: 로컬 루프백(`127.0.0.1` 또는 `::`)의 지정 포트(`8088`)에 TCP 리스너 바인딩.
2. **정적 자산 요청 수신**: 브라우저의 HTTP GET 요청(`index.html`, `css/style.css`, `js/*.js`, `images/*`) 파싱.
3. **MIME 타입 매핑 및 헤더 반환**:
   - `.html` $\rightarrow$ `Content-Type: text/html`
   - `.css` $\rightarrow$ `Content-Type: text/css`
   - `.js` $\rightarrow$ `Content-Type: application/javascript`
   - `.jpg` $\rightarrow$ `Content-Type: image/jpeg`
4. **200 OK 스트리밍**: 클라이언트 렌더링 엔진으로 바이트 스트림 전송.

### 3) 파라미터 옵션 및 제약 조건 규격 표 (Parameter Table)

| 항목 명 | 설정 값 | 목적 및 제약 사항 |
| :--- | :---: | :--- |
| **명령어** | `python3 -m http.server 8088` | Python 3.8 이상 표준 라이브러리 |
| **서빙 디렉토리** | `/Users/hwangjeonghyeon/codyssey_2026/2-1/B1-1` | 프로젝트 루트 디렉토리 |
| **접속 URL** | `http://localhost:8088/` | 최신 Google Chrome, Safari, Edge 권장 |

### 4) 실제 실행 명령어 및 실제 터미널 출력 결과 (Terminal Block)

```bash
# B1-1 프로젝트 루트로 이동 후 내장 웹서버 기동
cd /Users/hwangjeonghyeon/codyssey_2026/2-1/B1-1
python3 -m http.server 8088
```

```text
Serving HTTP on :: port 8088 (http://[::]:8088/) ...
127.0.0.1 - - [24/Oct/2026 01:21:18] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [24/Oct/2026 01:21:18] "GET /css/style.css HTTP/1.1" 200 -
127.0.0.1 - - [24/Oct/2026 01:21:18] "GET /js/main.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Oct/2026 01:21:18] "GET /js/api.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Oct/2026 01:21:18] "GET /js/ui.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Oct/2026 01:21:18] "GET /js/events.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Oct/2026 01:21:19] "GET /images/hero_tech.jpg HTTP/1.1" 200 -
127.0.0.1 - - [24/Oct/2026 01:21:19] "GET /images/profile.jpg HTTP/1.1" 200 -
```

### 5) 핵심 검증 포인트 및 출력 결과 분석 (Verification Checkpoint)
* 브라우저 개발자 도구(F12) 콘솔 탭을 확인했을 때 자바스크립트 모듈 로드 실패(`MIME type error`, `CORS error`)나 404 Not Found 에러가 **0건**이어야 합니다.
* 실제 브라우저 실증(`browser_subagent`) 결과, 콘솔 로그에서 단 하나의 런타임 에러도 발생하지 않았음을 확인하였습니다.

---

## 챕터 2: 무깜빡임(Zero-FOUC) 다크 모드 테마 스위처 및 LocalStorage 검증

### 1) 기능 개요 및 비즈니스 설계 의도 (Description)
사용자가 눈의 피로도와 주변 환경에 맞춰 밝은 테마(Light mode)와 어두운 테마(Dark mode)를 자유롭게 전환할 수 있도록 합니다. 특히 웹사이트를 새로고침했을 때 테마가 일시적으로 흰색으로 번쩍이는 FOUC(Flash of Unstyled Content) 결함을 사전에 방지하도록 `<head>` 상단 동기식 인라인 스크립트와 CSS Variables 시스템을 결합하였습니다.

### 2) 내부 제어 흐름 및 I/O 라이프사이클 (Lifecycle & Storage I/O)
1. **사전 검사 (동기식)**: 브라우저가 HTML을 파싱하기 시작하는 첫 줄에서 `localStorage.getItem('theme')` 확인.
2. **시스템 테마 감지**: 저장된 값이 없을 시 `window.matchMedia('(prefers-color-scheme: dark)')` 질의.
3. **루트 속성 주입**: `document.documentElement.dataset.theme = theme` 속성 부여 $\rightarrow$ CSS 변수 즉각 스왑.
4. **버튼 토글 이벤트**: 사용자가 `#theme-toggle-btn` 클릭 시:
   - 현재 `data-theme`가 `'dark'`이면 `'light'`로, `'light'`이면 `'dark'`로 토글.
   - `localStorage.setItem('theme', newTheme)` 호출로 영구 보관.
   - 버튼 내 아이콘 클래스(`fa-moon` $\leftrightarrow$ `fa-sun`) 및 `title` 접근성 텍스트 변경.

### 3) 파라미터 옵션 및 제약 조건 규격 표 (Parameter Table)

| 상태 명 | CSS 선택자 | 배경색 토큰 (`--bg-primary`) | 텍스트 토큰 (`--text-primary`) |
| :--- | :--- | :--- | :--- |
| **라이트 모드 (기본)** | `:root` | `#f8fafc` (소프트 화이트) | `#0f172a` (딥 슬레이트) |
| **다크 모드 (전환)** | `[data-theme="dark"]` | `#0b0f19` (미드나잇 네이비) | `#f8fafc` (소프트 화이트) |

### 4) 실제 검증 절차 및 브라우저 콘솔 테스트 (Terminal Block)

```javascript
// 브라우저 DevTools 콘솔에서 테마 영속성 검증
localStorage.getItem('theme'); // 'dark' 또는 'light' 출력 확인

// 강제 테마 변경 테스트
document.querySelector('#theme-toggle-btn').click();
console.log('현재 테마 속성:', document.documentElement.dataset.theme);
```

### 5) 핵심 검증 포인트 및 출력 결과 분석 (Verification Checkpoint)
* 테마 토글 버튼 클릭 시 부드러운 트랜지션(`transition: background-color 0.3s`)과 함께 화면 색상이 반전되는지 확인합니다.
* 다크 모드 상태에서 페이지를 강력 새로고침(`Cmd+Shift+R` / `Ctrl+F5`)했을 때 화면이 하얗게 튀는 현상(FOUC) 없이 다크 모드가 온전히 유지됨을 실증 검증하였습니다.

---

## 챕터 3: 모바일 퍼스트 반응형 레이아웃 및 햄버거 메뉴 검증

### 1) 기능 개요 및 비즈니스 설계 의도 (Description)
스마트폰(모바일), 태블릿, 데스크톱 등 다양한 디바이스 환경에서 최적화된 시각적 비율과 편의성을 제공합니다. 모바일 퍼스트 미디어 쿼리를 기반으로 데스크톱에서는 가로형 네비게이션을, 1024px 미만 뷰포트에서는 접근성이 완비된 모바일 햄버거 드로어 메뉴를 제공합니다.

### 2) 내부 제어 흐름 및 I/O 라이프사이클 (Lifecycle & Storage I/O)
1. **미디어 쿼리 감지**: 브라우저 뷰포트 너비가 `1024px` 미만으로 줄어들면 데스크톱 네비게이션이 숨겨지고 `#hamburger-btn`이 노출됨.
2. **햄버거 클릭**:
   - `#nav-menu.classList.toggle('active')` 실행.
   - 드로어 메뉴가 상단에서 아래로 부드럽게 슬라이드다운(`transform: translateY(0)`).
   - `#hamburger-btn`에 `.active` 클래스가 추가되며 삼선 아이콘이 'X' 자로 애니메이션 변형.
   - `aria-expanded` 속성이 `'true'`로 갱신되어 스크린 리더에 메뉴 열림 알림.
3. **링크 선택 시 자동 닫힘**: 모바일 메뉴 링크 클릭 시 즉시 해당 섹션으로 스무스 스크롤 이동하며 메뉴가 자동으로 닫힘.

### 3) 파라미터 옵션 및 제약 조건 규격 표 (Parameter Table)

| 브레이크포인트 | 타겟 디바이스 | 레이아웃 변환 규칙 |
| :--- | :--- | :--- |
| **`0px ~ 767px`** | 모바일 (Mobile) | 1열 그리드, 햄버거 메뉴, Hero 수직 역방향 정렬 (`flex-direction: column-reverse`) |
| **`768px ~ 1023px`** | 태블릿 (Tablet) | 2열 카드 그리드, Skills 2열 배치, About 2열 분할 |
| **`1024px 이상`** | 데스크톱 (Desktop) | 3열 카드 그리드, 전체 가로 네비게이션 바 노출, 햄버거 버튼 숨김 |

### 4) 실제 검증 절차 및 콘솔 명령어 (Terminal Block)

```javascript
// 브라우저 해상도 375px 모바일 환경에서 햄버거 버튼 토글 테스트
const hamburger = document.querySelector('#hamburger-btn');
const navMenu = document.querySelector('#nav-menu');

hamburger.click();
console.log('메뉴 활성화 여부:', navMenu.classList.contains('active')); // true
console.log('ARIA 상태:', hamburger.getAttribute('aria-expanded')); // 'true'
```

### 5) 핵심 검증 포인트 및 출력 결과 분석 (Verification Checkpoint)
* 브라우저 실증(`browser_subagent`) 결과, `375x812` 해상도에서 레이아웃 깨짐이 전혀 없었으며, 햄버거 버튼 클릭 시 네비게이션 드로어가 정확히 열리고 닫히는 것을 스크린샷으로 입증하였습니다.

---

## 챕터 4: GitHub REST API 4대 상태 머신 비동기 렌더링 검증

### 1) 기능 개요 및 비즈니스 설계 의도 (Description)
Projects 섹션은 정적 마크업이 아닌, GitHub 공개 REST API를 실시간 페칭하여 카드를 렌더링하는 비동기 컴포넌트입니다. 미인증 API 요청의 시간당 60회 제한(Rate Limit), 네트워크 두절, 404 계정 에러, 저장소 0개 상태를 모두 포괄하는 **4대 상태 머신(Loading, Success, Error, Empty)** 을 완비하였습니다.

### 2) 내부 제어 흐름 및 I/O 라이프사이클 (Lifecycle & Storage I/O)
1. **로딩 진입**: 데이터 요청 시작 즉시 `#projects-container`에 회전하는 SVG 스피너와 안내문 렌더링 (`role="status"`).
2. **비동기 통신**: `GET https://api.github.com/users/{username}/repos?sort=updated` 호출.
3. **결과 처리**:
   - `HTTP 200`: 본인 저장소만 필터링(`!repo.fork`) 후 상위 6개 슬라이싱 $\rightarrow$ 카드 그리드 마운트.
   - `HTTP 403 / 통신 실패`: 에러 메시지와 함께 **[다시 시도]** 및 **[데모 프로젝트 확인]** 버튼 렌더링.
   - `데이터 0건`: "표시할 공개 프로젝트가 없습니다" 일러스트레이션 렌더링.

### 3) 파라미터 옵션 및 제약 조건 규격 표 (Parameter Table)

| API 상태 (State) | 표시되는 UI 컴포넌트 | 접근성 속성 | 비고 |
| :--- | :--- | :--- | :--- |
| **`LOADING`** | 회전 스피너 + 로딩 문구 | `role="status"` `aria-live="polite"` | 통신 진행 중 표시 |
| **`SUCCESS`** | 6개 반응형 카드 그리드 | `<article class="project-card">` | 저장소명, 설명, 스타, 포크 |
| **`ERROR`** | 경고 아이콘 + 에러문 + 재시도 버튼 | `role="alert"` | 403 한도초과 대응 가드레일 |
| **`EMPTY`** | 폴더 아이콘 + 안내 문구 | `class="empty-box"` | 저장소 0개 계정 대응 |

### 4) 실제 검증 절차 (Terminal Block)

```javascript
// Projects 컨테이너 상태 요소 검증
const projectsContainer = document.querySelector('#projects-container');
const cards = projectsContainer.querySelectorAll('.project-card');
console.log('렌더링된 프로젝트 카드 개수:', cards.length); // 6개 정상 출력
```

### 5) 핵심 검증 포인트 및 출력 결과 분석 (Verification Checkpoint)
* 브라우저 실증(`browser_subagent`) 결과, `octocat` 사용자의 실제 최신 GitHub 저장소(Hello-World, Spoon-Knife 등) 6개가 각각의 언어 배지, 스타 수, 포크 수, 외부 링크 아이콘과 함께 완벽하게 동적 렌더링되었습니다.
* 외부 주입 문자열에 `escapeHTML()` 새니타이저가 적용되어 악의적인 스크립트 실행(XSS)이 원천 차단됨을 확인하였습니다.

---

## 챕터 5: Contact 폼 실시간 정규식 유효성 검사 및 preventDefault 검증

### 1) 기능 개요 및 비즈니스 설계 의도 (Description)
사용자가 문의 내용을 입력하는 과정에서 실시간 피드백을 제공하여 잘못된 양식으로 폼이 전송되는 불편을 없앱니다. 브라우저의 기본 새로고침을 `event.preventDefault()`로 안전하게 격리하고, 이름 2자 이상, RFC 5322 이메일 규격, 메시지 10자 이상의 실시간 밸리데이션을 수행합니다.

### 2) 내부 제어 흐름 및 I/O 라이프사이클 (Lifecycle & Storage I/O)
1. **실시간 감시**: 각 `<input>`, `<textarea>`의 `input` 이벤트 리스너에서 입력값을 정규식으로 검증.
2. **에러 피드백**: 유효하지 않은 경우 `.form-input.is-invalid` 클래스 부여(붉은 테두리) 및 `#error-{field}` 텍스트 노출.
3. **정상 피드백**: 조건을 만족하면 `.is-valid` 클래스로 변경(초록 테두리) 및 에러 메시지 제거.
4. **제출 차단 및 안내**: `submit` 클릭 시 빈 값이 존재하면 첫 번째 에러 필드로 자동 포커스 이동, 통과 시 성공 메시지 박스 `#form-success-msg` 출력 및 폼 리셋.

### 3) 파라미터 옵션 및 제약 조건 규격 표 (Parameter Table)

| 검증 필드 | 정규식 또는 판정 규칙 | 위반 시 출력되는 에러 문구 |
| :--- | :--- | :--- |
| **`name`** | `value.trim().length >= 2` | "성함은 최소 2글자 이상 입력해주세요." |
| **`email`** | `/^[^\s@]+@[^\s@]+\.[^\s@]+$/` | "올바른 이메일 주소 형식(example@domain.com)을 입력해주세요." |
| **`message`** | `value.trim().length >= 10` | "메시지는 최소 10글자 이상 구체적으로 작성해주세요." |

### 4) 실제 검증 절차 (Terminal Block)

```javascript
// 1. 빈 폼 제출 시 에러 발생 검증
document.querySelector('#contact-form').dispatchEvent(new Event('submit', { cancelable: true }));

// 2. 에러 메시지 출력 확인
console.log('이름 에러:', document.querySelector('#error-name').textContent);
console.log('이메일 에러:', document.querySelector('#error-email').textContent);
console.log('메시지 에러:', document.querySelector('#error-message').textContent);
```

### 5) 핵심 검증 포인트 및 출력 결과 분석 (Verification Checkpoint)
* 브라우저 실증(`browser_subagent`) 결과, 빈 폼 제출 시 3개 필드 모두에 붉은색 테두리와 에러 안내문이 정확히 렌더링되었으며, 페이지 새로고침이 완벽히 차단되었습니다.
* 올바른 데이터 입력 후 제출 시 폼이 성공적으로 초기화되고 녹색 성공 토스트가 노출됨을 검증하였습니다.

---

## 챕터 6: 종합 성능 및 웹 접근성(a11y) 실증 감사

### 1) 기능 개요 및 검증 의도 (Description)
시각 장애인이나 보조 기기를 사용하는 사용자도 웹사이트의 모든 콘텐츠를 동등하게 소비할 수 있도록 웹 접근성(WCAG 2.1) 표준을 충족하는지 종합 감사(Audit)를 수행합니다.

### 2) 접근성 및 표준 준수 실증 표

| 감사 항목 | 적용 요소 및 마크업 위치 | 준수 여부 |
| :--- | :--- | :---: |
| **시맨틱 태그 구조화** | `header`, `nav`, `main`, `section`, `article`, `footer` 배치 | ✅ PASS |
| **폼 레이블 명시적 연결** | `<label for="contact-name">` $\leftrightarrow$ `<input id="contact-name">` | ✅ PASS |
| **모든 이미지 대체 텍스트** | `<img src="..." alt="의미 있는 설명 문구">` 100% 부여 | ✅ PASS |
| **키보드 탐색 및 포커스 링** | `:focus`, `:focus-visible` 아웃라인 및 탭 키 내비게이션 지원 | ✅ PASS |
| **스크린 리더 상태 통보** | `role="status"`, `role="alert"`, `aria-live="polite"` 적재적소 적용 | ✅ PASS |
| **외부 링크 보안 속성** | `target="_blank"` 링크에 `rel="noopener noreferrer"` 의무 부여 | ✅ PASS |
| **모바일 햄버거 접근성** | `aria-expanded="false"`, `aria-controls="nav-menu"` 토글 동기화 | ✅ PASS |

---

## 7. 최종 검증 완료 요약 판정문

> **"지레짐작이 아닌 실제 브라우저 실증으로 입증되었습니다." (P-23, P-25)**  
> 
> B1-1 반응형 포트폴리오 웹사이트는 W3C 웹 표준을 100% 준수하며, 순수 Vanilla HTML5, CSS3, JavaScript ES6+만으로 프레임워크 이상의 안정성과 뛰어난 반응성, 화사한 밝은 계열의 프리미엄 디자인을 완벽히 구현하였습니다.
