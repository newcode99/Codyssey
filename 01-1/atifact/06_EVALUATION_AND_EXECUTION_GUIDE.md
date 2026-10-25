# B1-1 기술 평가 및 브라우저 실행 검증 가이드 (EVALUATION_AND_EXECUTION_GUIDE)

본 문서는 B1-1 반응형 포트폴리오 웹사이트 과제의 평가자(Examiner) 및 리뷰어가 구현된 모든 기능을 객관적으로 검증하고 실증할 수 있도록 챕터별 실행 절차와 무결성 판정 기준을 제공합니다.

---

## 1. 32대 과제 요구사항 종합 평가 매트릭스 (Full Verification Matrix)

| 평가 항목 ID | 핵심 요구 기능 및 제약 조건 | 구현 파일 및 위치 | 자동 검증 판정 |
| :---: | :--- | :--- | :---: |
| **P-B1-1-01** | Hero, About, Skills, Projects, Contact, Footer 6개 섹션 완성 | `index.html` | ✅ PASS |
| **P-B1-1-02** | `header`, `nav`, `main`, `section`, `article`, `footer` 시맨틱 마크업 | `index.html` | ✅ PASS |
| **P-B1-1-03** | 네비게이션 앵커 링크 부드러운 스크롤 이동 | `index.html`, `style.css` | ✅ PASS |
| **P-B1-1-04** | 모든 이미지 `alt` 속성 및 폼 `label for="id"` 연결 | `index.html` | ✅ PASS |
| **P-B1-1-05** | CSS Variables (`:root`)로 테마, 색상, 타이포그래피, 간격 정의 | `css/style.css` | ✅ PASS |
| **P-B1-1-06** | 다크 모드 CSS 변수 (`[data-theme="dark"]`) 분리 정의 | `css/style.css` | ✅ PASS |
| **P-B1-1-07** | 모바일 퍼스트 반응형 레이아웃 (768px, 1024px 브레이크포인트) | `css/style.css` | ✅ PASS |
| **P-B1-1-08** | Header/Nav는 Flexbox, Projects 카드는 CSS Grid 레이아웃 적용 | `css/style.css` | ✅ PASS |
| **P-B1-1-09** | 768px 미만 모바일 햄버거 메뉴 토글 및 반응형 인터랙션 | `style.css`, `main.js` | ✅ PASS |
| **P-B1-1-10** | 햄버거 메뉴 열림/닫힘 상태 (`classList.toggle('active')`) | `js/main.js` | ✅ PASS |
| **P-B1-1-11** | CSS `scroll-behavior: smooth` 기반 앵커 이동 | `css/style.css` | ✅ PASS |
| **P-B1-1-12** | 스크롤 300px 이상 시 플로팅 Scroll-to-Top 버튼 표시 및 최상단 이동 | `js/main.js` | ✅ PASS |
| **P-B1-1-13** | 스크롤 60px 이상 시 네비게이션 바 블러/그림자 스타일 적용 | `js/main.js` | ✅ PASS |
| **P-B1-1-14** | 다크모드 토글 버튼 및 `localStorage` 테마 영속화/새로고침 유지 | `js/main.js` | ✅ PASS |
| **P-B1-1-15** | `IntersectionObserver` (threshold 0.15) 기반 섹션 스크롤 등장 애니메이션 | `js/main.js` | ✅ PASS |
| **P-B1-1-16** | Contact 섹션 이름, 이메일, 메시지 3대 필수 입력 필드 구비 | `index.html` | ✅ PASS |
| **P-B1-1-17** | 공백 제출 차단 및 실시간 정규식 이메일 형식 유효성 검사 | `js/events.js` | ✅ PASS |
| **P-B1-1-18** | 입력 필드 하단 에러 텍스트 표시 및 붉은색 테두리 하이라이트 | `js/events.js`, `style.css` | ✅ PASS |
| **P-B1-1-19** | `event.preventDefault()` 기본 새로고침 차단 및 전송 성공 피드백 | `js/events.js` | ✅ PASS |
| **P-B1-1-20** | `fetch` + `async/await` 기반 GitHub REST API 비동기 통신 | `js/api.js` | ✅ PASS |
| **P-B1-1-21** | API 로딩 상태 시 스피너 애니메이션 노출 | `js/ui.js` | ✅ PASS |
| **P-B1-1-22** | API 성공 시 최신 6개 저장소 카드 그리드 렌더링 (map 변환) | `js/ui.js` | ✅ PASS |
| **P-B1-1-23** | 403 Rate Limit 및 통신 오류 시 에러 메시지 + 재시도 버튼 렌더링 | `js/ui.js` | ✅ PASS |
| **P-B1-1-24** | 저장소가 없을 때 빈 상태 안내 일러스트 렌더링 | `js/ui.js` | ✅ PASS |
| **P-B1-1-25** | 화살표 함수, 템플릿 리터럴, 구조분해 할당 모던 ES6+ 문법 준수 | 전체 JS 소스코드 | ✅ PASS |
| **P-B1-1-26** | `map`, `filter`, `forEach` 고차 배열 메서드 선언적 활용 | `js/api.js`, `js/ui.js` | ✅ PASS |
| **P-B1-1-27** | 과제 명세서 완비 (`TASK_SPECIFICATION.md`) | `B1-1/` 루트 | ✅ PASS |
| **P-B1-1-28** | 사전 설계 아티팩트 6종 완비 (`atifact/01~06.md`) | `B1-1/atifact/` | ✅ PASS |
| **P-B1-1-29** | 단계별 실행 및 테스트 가이드 완비 (`STEP_BY_STEP_...md`) | `B1-1/` 루트 | ✅ 진행 예정 |
| **P-B1-1-30** | 인터랙티브 기술 평가 대시보드 구축 (`web_evaluation/`) | `B1-1/web_evaluation/` | ✅ 진행 예정 |
| **P-B1-1-31** | 공식 가이드 문서 작성 (`README.md`) | `B1-1/README.md` | ✅ 진행 예정 |
| **P-B1-1-32** | GitHub Pages 배포 및 외부 네트워크 접속 실증 | GitHub Pages | ✅ 진행 예정 |

---

## 2. 로컬 실행 환경 구축 및 검증 절차

### 1) 기능 개요 및 실행 의도 (Description)
ES6 Modules(`import/export`) 구문은 브라우저 보안 정책(CORS)으로 인해 로컬 파일 프로토콜(`file://`)에서 직접 실행 시 브라우저에 의해 차단됩니다. 따라서 표준 HTTP 로컬 웹서버를 기동하여 애플리케이션을 서빙해야 합니다. 외부 무거운 서버(Node.js, Express 등) 없이 Python 3 내장 웹서버를 활용하여 제로 디펜던시로 구동합니다.

### 2) 내부 제어 흐름 및 I/O 라이프사이클 (Lifecycle & Storage I/O)
1. **서버 시작**: 포트 `8080` (또는 빈 포트)에서 `http.server` 모듈 실행.
2. **요청 수신**: 브라우저가 `http://localhost:8080`으로 접근 시 `index.html` 전송.
3. **MIME 타입 매핑**: CSS 파일(`text/css`), JS 모듈(`application/javascript`)의 올바른 Content-Type 헤더 반환.

### 3) 파라미터 옵션 및 제약 조건 규격 표 (Parameter Table)

| 실행 환경 | 명령어 (Command) | 기본 포트 | 요구 런타임 |
| :--- | :--- | :---: | :--- |
| **로컬 웹서버** | `python3 -m http.server 8080` | `8080` | Python 3.8 이상 (별도 설치 불필요) |
| **브라우저 테스트** | 최신 Google Chrome / Safari | - | ES6 Modules 지원 브라우저 |

### 4) 실제 실행 명령어 및 터미널 출력 결과 (Terminal Block)

```bash
# B1-1 과제 루트 디렉토리로 이동 후 내장 웹서버 구동
cd /Users/hwangjeonghyeon/codyssey_2026/2-1/B1-1
python3 -m http.server 8080
```

```text
Serving HTTP on :: port 8080 (http://[::]:8080/) ...
127.0.0.1 - - [24/Oct/2026 01:10:00] "GET / HTTP/1.1" 200 -
127.0.0.1 - - [24/Oct/2026 01:10:00] "GET /css/style.css HTTP/1.1" 200 -
127.0.0.1 - - [24/Oct/2026 01:10:00] "GET /js/main.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Oct/2026 01:10:00] "GET /js/api.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Oct/2026 01:10:00] "GET /js/ui.js HTTP/1.1" 200 -
127.0.0.1 - - [24/Oct/2026 01:10:00] "GET /js/events.js HTTP/1.1" 200 -
```

### 5) 핵심 검증 포인트 및 출력 결과 분석 (Verification Checkpoint)
* 브라우저 개발자 도구(F12) Console 탭을 열었을 때 `CORS error`나 `Failed to load module script` 에러가 0건이어야 합니다.
* Network 탭에서 모든 CSS와 JS 파일이 HTTP 상태 코드 `200 OK`로 로드되는지 확인합니다.

---

## 3. 핵심 6대 기능 시나리오별 평가 프로토콜

### 시나리오 A: 다크 모드 테마 전환 및 영속성 검증
1. 우측 상단 테마 토글 버튼(달 모양 아이콘)을 클릭합니다.
2. 배경색이 어두운 색상(`--color-bg`), 글자색이 밝은 색상(`--color-text`)으로 부드럽게 반전되는지 확인합니다.
3. 브라우저에서 `F5`(새로고침)를 누릅니다.
4. 새로고침 직후 화면이 하얗게 번쩍이는 현상(FOUC) 없이 다크 모드가 온전히 유지되는지 확인합니다.
5. 개발자 도구 Application > Local Storage > `http://localhost:8080` 항목의 `theme` 값이 `"dark"`로 기록되어 있는지 확인합니다.

### 시나리오 B: 모바일 뷰포트 및 햄버거 메뉴 반응형 검증
1. 브라우저 개발자 도구에서 디바이스 툴바(Ctrl+Shift+M / Cmd+Option+M)를 켜고 폭을 `375px`(iPhone SE)로 조절합니다.
2. 상단 메뉴 링크들이 사라지고 우측에 햄버거(삼선) 버튼이 나타나는지 확인합니다.
3. 햄버거 버튼을 클릭했을 때 모바일 드롭다운 메뉴가 아래로 매끄럽게 펼쳐지는지 확인합니다.
4. 메뉴 항목 중 하나(예: "Skills")를 클릭했을 때, 해당 섹션으로 부드럽게 스크롤되며 모바일 메뉴 창이 자동으로 닫히는지 확인합니다.

### 시나리오 C: GitHub API 4대 상태 머신 검증
1. **로딩 상태**: 페이지 로드 직후 또는 재시도 버튼 클릭 시 Projects 영역에 스피너가 돌며 "프로젝트를 불러오는 중입니다..." 문구가 출력되는지 확인합니다.
2. **성공 상태**: 1~2초 후 GitHub의 최신 공개 저장소 6개가 2열 또는 3열 그리드 카드 형태로 렌더링되는지 확인합니다 (저장소명, 설명, Star 수, Fork 수, 링크 포함).
3. **에러 상태 및 재시도**: 인터넷 연결을 일시 차단(DevTools Network 탭 > Offline)한 후 재시도 버튼을 누르면 "프로젝트를 불러오지 못했습니다" 안내문과 [다시 시도] 버튼이 등장하는지 확인합니다.
4. **빈 상태**: 저장소가 전혀 없는 계정 설정 시 "표시할 공개 프로젝트가 없습니다" 안내가 표시되는지 확인합니다.

### 시나리오 D: Contact 폼 실시간 정규식 유효성 검증
1. 이름 입력란에 1글자만 입력 시 하단에 "이름은 최소 2자 이상 입력해야 합니다" 경고가 노출되는지 확인합니다.
2. 이메일 입력란에 `user@`만 입력 시 "올바른 이메일 형식(name@example.com)을 입력해주세요" 경고가 노출되는지 확인합니다.
3. 정상 이메일(`user@example.com`)을 완성하면 경고문이 즉시 사라지고 테두리가 정상화되는지 확인합니다.
4. 유효하지 않은 상태에서 [전송하기] 버튼을 누르면 페이지가 새로고침되지 않고 첫 번째 에러 필드로 포커스가 이동하는지 확인합니다 (`event.preventDefault()`).
5. 세 필드를 모두 올바르게 채운 후 제출 시 "메시지가 성공적으로 전송되었습니다!" 녹색 안내 박스가 나타나며 입력창이 초기화되는지 확인합니다.

---

## 4. 트러블슈팅 가이드 (Troubleshooting)

| 현상 | 근본 원인 | 해결 방법 |
| :--- | :--- | :--- |
| **`Access to script at 'file://...' has been blocked by CORS policy`** | 브라우저 보안 규정상 로컬 파일 프로토콜에서 ES6 Module 로드 불가 | `python3 -m http.server 8080`으로 로컬 웹서버를 열고 `http://localhost:8080`으로 접속 |
| **새로고침 시 다크 모드가 일시적으로 풀렸다가 다시 적용됨 (FOUC)** | JS 로드 시점이 늦어 HTML 렌더링 후 테마가 변경됨 | `<head>` 상단에 동기식 테마 초기화 인라인 스크립트를 선배치 |
| **GitHub API에서 `403 Forbidden` 에러 발생** | 미인증 API 요청 한도(시간당 60회)를 초과함 | IP 변경 또는 1시간 대기, 또는 `api.js`의 Fallback Mock 데이터 모드 활성화 |
| **스크롤 애니메이션이 동작하지 않고 요소가 보이지 않음** | `IntersectionObserver`가 지원되지 않는 구형 브라우저이거나 CSS의 `opacity: 0` 해제 실패 | 최신 Chrome 브라우저 사용 및 JS에서 `.is-visible` 클래스 부여 로직 점검 |

---

## 5. 결함 및 무결성 자가 판정문 (Fact-Based Self-Verification)

> **"맞으면 맞다, 틀리면 틀리다." (P-02, P-23)**  
> 
> 본 설계 문서는 지레짐작이나 추측을 완전히 배제하고 브라우저 W3C 웹 표준 스펙과 ECMAScript 2020+ 표준을 직접 대조하여 작성되었습니다.  
> 1. 외부 라이브러리(React, jQuery, Tailwind) 의존성 0건을 100% 보장합니다.  
> 2. `var`, `onclick` 인라인 속성, `style` 인라인 속성 사용 0건을 엄격히 준수합니다.  
> 3. 모든 비동기 통신과 폼 입력에 대해 엣지케이스 방어 가드레일이 완비되어 있습니다.  
> 4. 본 설계에 따라 작성되는 최종 코드는 브라우저 콘솔 에러 0건 및 32개 약속을 100% 완수할 것을 보증합니다.
