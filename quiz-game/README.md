# Python-Practice: Console Quiz Game (OOP)

객체지향 프로그래밍(OOP) 원칙과 견고한 예외 처리 메카니즘이 적용된 터미널 기반 퀴즈 게임 프로젝트임.

## 1. 프로젝트 구조
```text
quiz-game/
├── main.py      # 최상위 진입점 및 비상 예외 방어 (Dome)
├── game.py      # 게임 엔진, RAM 상태 관리 및 아토믹 저장 (Brain)
├── quiz.py      # 단일 퀴즈 데이터 캡슐화 및 직렬화 (Model)
├── utils.py     # 사용자 입력 정제 및 필터링 (Filter)
└── state.json   # 퀴즈 및 히스토리 영구 저장 데이터 (JSON)
```

## 2. 핵심 설계 철학
*   **Encapsulation (캡슐화)**: `Quiz` 클래스는 자신의 데이터 검증과 변환을 스스로 책임짐.
*   **Information Expert (정보 전문가)**: 딕셔너리를 객체로 조립하는 로직은 오직 `Quiz` 내부의 `from_dict`에만 전담함.
*   **Atomic Write (원자적 쓰기)**: `os.replace`를 사용하여 파일 저장 중 발생할 수 있는 데이터 오염을 방지함.
*   **Unified Exception Shield**: `utils`에서 발생한 비상 신호를 상위로 전결(`raise`)하여 `main`에서 통합 관리함.

## 3. 주요 기능
*   **퀴즈 관리**: 추가(중도 취소 가능), 조회(번호 기반), 삭제 기능 제공함.
*   **플레이 시스템**: 순차 출제, 오답 시 자동 스킵, 중도 포기 및 부분 정산 기능 제공함.
*   **기록 관리**: 역대 최고 점수 갱신 및 날짜별 플레이 히스토리 기록함.

## 4. 실행 방법
```bash
cd quiz-game
python main.py
```

## 5. 깃 전략 (Commit Strategy)
총 14단계의 세분화된 커밋 전략을 통해 개발 과정의 정합성과 추적성을 확보하였음.
