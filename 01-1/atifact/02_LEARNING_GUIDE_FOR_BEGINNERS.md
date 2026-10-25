# B1-1 초심자를 위한 모던 바닐라 웹 개념 완전 학습서 (LEARNING_GUIDE_FOR_BEGINNERS)

본 문서는 웹 개발에 처음 입문하는 학습자가 브라우저의 동작 원리와 프론트엔드의 기초를 완벽히 이해할 수 있도록 **실생활 비유 → 기술 매핑 → 실제 동작 코드**의 3단계로 핵심 개념을 해설합니다.

---

## 1. 웹 프론트엔드의 3대 기둥 — 인체 건축학 비유

### 1.1 태초의 질문: "HTML, CSS, JavaScript는 왜 따로 존재할까요?"

한 파일에 모든 것을 섞어서 쓸 수도 있는데, 왜 웹 개발자들은 이 세 가지를 철저히 구분해서 작업할까요? 그것은 **사람의 몸(건축물)** 을 만드는 이치와 완전히 같기 때문입니다.

| 웹 기술 | 인체 비유 | 건축 비유 | 핵심 역할과 존재 이유 |
| :--- | :--- | :--- | :--- |
| **HTML** | **뼈대(골격)** | 기둥과 벽체 | 어디에 머리가 있고 팔이 있는지, 무엇이 제목이고 본문인지 **의미와 구조**를 정의함. |
| **CSS** | **피부와 옷(외모)** | 페인트와 인테리어 | 눈의 색상, 옷의 핏, 여백, 모바일 크기에 맞는 옷 갈아입기 등 **시각적 스타일**을 담당함. |
| **JavaScript** | **근육과 신경망(동작)** | 전등 스위치와 엘리베이터 | 손을 흔들고, 눈을 깜빡이고, 외부 자극(클릭)에 반응하여 **살아 움직이는 인터랙션**을 부여함. |

```
[인체 건축학 매핑 다이어그램]
 ┌────────────────────────────────────────────────────────┐
 │ HTML  : <button id="btn">클릭하세요</button>              │ ── 버튼이라는 뼈대 생성
 ├────────────────────────────────────────────────────────┤
 │ CSS   : #btn { background: royalblue; border-radius: 8px; }│ ── 푸른색 옷과 둥근 모서리 입히기
 ├────────────────────────────────────────────────────────┤
 │ JS    : btn.addEventListener('click', () => alert('안녕!'));│ ── 클릭했을 때 인사하는 신경망 연결
 └────────────────────────────────────────────────────────┘
```

---

## 2. DOM(Document Object Model) — 브라우저 속 가계도 비유

### 2.1 DOM이란 무엇인가?
HTML 문서는 단순한 텍스트 파일에 불과합니다. 하지만 브라우저가 이 텍스트를 읽는 순간, 브라우저는 이것을 부모-자식 관계가 얽힌 거대한 **가계도(Tree 구조)** 형태의 자바스크립트 객체로 변환합니다. 이것을 **DOM**이라고 부릅니다.

* **실생활 비유**: 회사의 조직도나 집안의 족보를 생각하면 됩니다. 할아버지(`<html>`) 아래에 아버지들(`<head>`, `<body>`)이 있고, 그 아래 자식들(`<section>`, `<p>`)이 있습니다.

### 2.2 `querySelector` — 이름표로 사람을 찾는 사내 방송
자바스크립트가 화면을 바꾸려면 먼저 "누구를 바꿀 것인가"를 찾아내야 합니다.

```javascript
// 1. 단일 요소 찾기 (가장 먼저 발견된 1명만 호출)
const header = document.querySelector('header');
const themeBtn = document.querySelector('#theme-toggle'); // ID 이름표(#)로 찾기

// 2. 다중 요소 찾기 (해당하는 모든 사람을 모아서 명부(NodeList)로 반환)
const navLinks = document.querySelectorAll('.nav-link');  // Class 이름표(.)로 찾기
navLinks.forEach(link => {
  console.log(link.textContent); // 각 링크의 글자 출력
});
```

---

## 3. 이벤트와 리스너 — 초인종과 센서등 비유

### 3.1 사용자의 행동은 모두 "사건(Event)"이다
마우스를 클릭하는 것(`click`), 키보드를 누르는 것(`input`), 마우스 휠을 굴리는 것(`scroll`), 화면 크기를 줄이는 것(`resize`) 등 사용자의 모든 움직임은 브라우저 안에서 **이벤트 신호**를 발생시킵니다.

### 3.2 `addEventListener` — 현관문에 센서등 달기
자바스크립트는 스스로 언제 클릭이 일어날지 미래를 알 수 없습니다. 그래서 특정 요소에 **"감시자(Listener)"** 를 달아두고, 해당 사건이 터졌을 때 실행할 **행동(Callback 함수)** 을 등록해 둡니다.

```
[초인종 비유 흐름도]
[방문객 손가락] ──(누른다: 'click' 이벤트)──▶ [초인종 버튼]
                                                    │
                                             (감시자 작동)
                                                    ▼
                                          [딩동 소리 재생 함수 실행]
```

```javascript
// 실제 코드: 버튼에 클릭 감시자 부착
const themeToggleBtn = document.querySelector('#theme-toggle');

themeToggleBtn.addEventListener('click', (event) => {
  // 이벤트 객체(event): 사건에 대한 모든 정보(클릭한 좌표, 타겟 요소 등)를 담고 있음
  console.log('초인종이 울렸습니다! 타겟:', event.target);
  document.body.classList.toggle('dark-theme');
});
```

---

## 4. CSS Flexbox vs Grid — 1차원 줄서기 vs 2차원 바둑판 비유

많은 초심자들이 Flexbox와 Grid 중 무엇을 써야 할지 혼란스러워합니다. 명쾌한 구분 기준은 **"차원(Dimension)"** 입니다.

| 구분 | Flexbox (1차원) | CSS Grid (2차원) |
| :--- | :--- | :--- |
| **비유** | **기차 칸 연결, 한 줄로 서서 번호 매기기** | **체스판, 바둑판, 아파트 단지 배치** |
| **제어 축** | 가로(Row) 또는 세로(Column) 중 **단 하나의 축** | 가로 행(Row)과 세로 열(Column)을 **동시에 제어** |
| **주요 용도** | 네비게이션 메뉴바, 버튼 안 아이콘+텍스트 정렬 | 프로젝트 카드 갤러리 그리드, 전체 대시보드 레이아웃 |
| **핵심 속성** | `display: flex; justify-content: space-between;` | `display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));` |

### 4.1 실제 코드 비교

```css
/* 1. Flexbox: 네비게이션 로고와 메뉴를 양쪽 끝으로 한 줄 정렬 */
.navbar {
  display: flex;
  justify-content: space-between; /* 왼쪽 끝 로고, 오른쪽 끝 메뉴 */
  align-items: center;            /* 세로축 가운데 정렬 */
}

/* 2. Grid: 프로젝트 카드를 화면 너비에 맞춰 자동으로 2열, 3열로 쪼개기 */
.projects-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem; /* 카드 사이 간격 */
}
```

---

## 5. 비동기(Async)와 Fetch API — 식당 진동벨과 배달 비유

### 5.1 동기(Sync) vs 비동기(Async)의 치명적 차이
* **동기(Synchronous)**: 카페에서 앞 손님의 커피가 나올 때까지 뒤 손님 주문을 일체 받지 않고 줄 전체를 멈추게 하는 방식 (브라우저가 멈춤, 화면 렉 발생).
* **비동기(Asynchronous)**: 주문을 받자마자 **"진동벨(Promise)"** 을 건네주고 다음 손님 주문을 받으며, 커피가 다 완성되었을 때 진동벨이 울리면 커피를 가져가는 방식.

### 5.2 `fetch`와 `async / await` — 가장 깔끔한 진동벨 수령법

```javascript
// GitHub 서버에서 프로젝트 목록을 비동기로 가져오는 함수
async function fetchProjects(username) {
  try {
    // 1. 주문 넣기 (진동벨 받기: 통신 시작)
    const response = await fetch(`https://api.github.com/users/${username}/repos`);
    
    // 2. HTTP 응답 상태 확인 (404나 403이면 에러 발생)
    if (!response.ok) {
      throw new Error(`서버 응답 오류 (상태코드: ${response.status})`);
    }

    // 3. 진동벨이 울리고 JSON 음식이 도착함
    const data = await response.json();
    return data; // 실제 프로젝트 배열 반환

  } catch (error) {
    // 네트워크 단절이나 API 한도 초과 시 처리
    console.error('데이터 수령 실패:', error.message);
    throw error; // 에러를 상위 UI 모듈로 전달
  }
}
```

---

## 6. LocalStorage — 브라우저가 간직하는 영구 비밀 메모장

사용자가 브라우저를 껐다 켜거나 새로고침했을 때, "내가 다크 모드를 선택했다"는 사실을 브라우저는 어떻게 기억할까요?
서버에 저장하지 않고도 내 컴퓨터 브라우저 안에 반영구적으로 Key-Value 텍스트를 적어둘 수 있는 공간이 **`localStorage`** 입니다.

```javascript
// 1. 저장하기 (불 끄고 자기 전에 메모)
localStorage.setItem('theme', 'dark');

// 2. 꺼내보기 (다음 날 아침에 확인)
const savedTheme = localStorage.getItem('theme'); // 'dark'

// 3. 지우기
localStorage.removeItem('theme');
```

---

## 7. 초심자가 가장 많이 하는 질문 TOP 5 (FAQ)

### Q1. `var`는 왜 쓰면 안 되고, `const`와 `let`만 써야 하나요?
> **답변**: `var`는 과거 자바스크립트 초창기에 만들어진 변수로, 변수가 선언되기 전에 호출되어도 에러가 나지 않는 기괴한 **호이스팅(Hoisting)** 현상이 일어나고, 함수 블록이 아니면 중괄호(`{}`)를 무시하여 변수 값이 덮어씌워지는 심각한 버그를 유발합니다.  
> 반면 `const`(재할당 불가 상수)와 `let`(재할당 가능 변수)은 엄격한 블록 스코프(`{}`)를 지키며 예기치 않은 데이터 변조를 원천 차단합니다. **실무에서는 90% 이상 `const`를 기본으로 쓰고, 반복문 카운터처럼 값이 변할 때만 `let`을 씁니다.**

### Q2. 왜 HTML에 `onclick="doSomething()"`을 직접 쓰면 안 되나요?
> **답변**: 이를 **인라인 이벤트 핸들러**라고 부르며, 구조(HTML)와 로직(JS)이 뒤섞여 유지보수가 불가능해집니다. 또한 하나의 버튼에 여러 개의 동작을 추가할 수 없고, 보안 정책(CSP: Content Security Policy)에서도 인라인 스크립트는 해킹 위험으로 간주되어 차단됩니다. 따라서 반드시 JS 파일 안에서 `element.addEventListener()`를 통해 깔끔하게 분리해야 합니다.

### Q3. `IntersectionObserver`는 기존 `window.onscroll`보다 왜 훨씬 좋은가요?
> **답변**: `window.addEventListener('scroll', ...)`은 스크롤할 때마다 1초에 수백 번씩 함수가 무자비하게 호출되어 브라우저 성능을 갉아먹고 화면을 버벅이게 만듭니다(Jank 현상).  
> 반면 `IntersectionObserver`는 브라우저 내부 렌더링 엔진이 백그라운드에서 "특정 요소가 화면에 20% 들어왔는가?"를 직접 계산하여 딱 그 순간에만 효율적으로 알려주므로 CPU 소모가 거의 없습니다.

### Q4. `event.preventDefault()`는 정확히 무엇을 막아주나요?
> **답변**: HTML 태그 중 일부는 태어날 때부터 브라우저 고유의 기본 동작을 가집니다. 예컨대 `<form>` 안의 제출 버튼을 누르면 페이지 전체가 깜빡이며 새로고침되고, `<a>` 링크를 누르면 URL이 즉시 이동합니다.  
> `event.preventDefault()`는 이러한 **브라우저의 기본 새로고침/이동 동작을 일시 정지**시키고, 우리가 만든 자바스크립트 유효성 검사 로직이나 비동기 통신이 먼저 실행될 수 있도록 제어권을 확보해 줍니다.

### Q5. GitHub API 호출 시 "403 Forbidden" 에러가 뜨는 이유는 무엇인가요?
> **답변**: GitHub REST API는 로그인(토큰) 없이 호출할 경우, 한 사람(하나의 IP)당 **시간당 최대 60회**까지만 요청을 허용합니다. 개발 중 페이지를 너무 자주 새로고침하면 60회를 금방 소진하여 403 에러가 발생합니다.  
> 따라서 견고한 애플리케이션은 403 에러가 났을 때 사용자에게 "API 호출 한도가 초과되었습니다. 잠시 후 다시 시도해주세요"라는 친절한 에러 UI를 띄우거나, 백업용 Mock(임시) 데이터를 표시하도록 방어벽을 세워야 합니다.
