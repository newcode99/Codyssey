# [Technical Specification] 파이썬 전문 퀴즈 시스템 (Console Quiz Game)

본 문서는 파이썬 객체지향(OOP)의 근본 원리와 데이터 무결성(Data Integrity)을 보장하기 위한 아키텍처 설계를 기술한 기술 명세서임.

---

## Ⅰ. 시스템 아키텍처 및 설계 단계

### [설계 6단계 프로세스]
1. **1단계 → 파일 구조**: `main.py`, `game.py`, `quiz.py`, `utils.py` 분리하여 관리의 효율성 극대화.
2. **2단계 → 책임 분리**: SRP(단일 책임 원칙)에 따라 하나의 클래스는 하나의 기능 담당에만 집중함.
3. **3단계 → 데이터 흐름**: JSON → 팩토리 로직 → RAM 적재 → 로직 실행 → 아토믹 저장의 무결성 순환 구조.
4. **4단계 → 연결 관계**: `Quiz` 클래스의 의존성 차단을 위해 `from_dict` 팩토리 메서드 활용함.
5. **5단계 → 예외 케이스**: `FileNotFound`, `DecodeError` 등 파일 시스템 예외에 대한 대응 로직 구축.
6. **6단계 → 데이터 스키마**: `best_score`, `history`, `quizzes` 등 JSON 스키마 구조 확정.

---

## Ⅱ. 핵심 설계 철학 (Philosophical Foundations)

### 1. 로그라이크(Roguelike)형 무결성 설계

- **절차적 설계: 1회 플레이 세션을 완전히 독립시켜 이전 세션의 오염을 남기지 않음.**
    - **[기술적 해석]**: 실행 중인 메모리 상태를 영구 저장소와 분리하여 세션 간 독립성을 확보함.
    - **[구현 코드]**: `game.py`의 `play_quiz` 내 로컬 변수 기반 점수 관리
    ```python
    current_score = 0 # 세션 독립성을 보장하는 지역 변수 스코어링
    for quiz in self.quizzes:
        ...
    ```

- **무결 상태 초기화: 에러 발생 시 즉시 처음부터 다시 실행 가능한 등가성(Idempotency) 확보함.**
    - **[기술적 해석]**: 런타임 오류 시 시스템을 마지막 안전 상태(Safe State)로 복구하는 복원력을 의미함.
    - **[구현 코드]**: `game.py`의 `load_state` 내 예외 처리 및 백업 격리
    ```python
    except (json.JSONDecodeError, KeyError):
        backup_path = self.data_path + ".bak"
        os.replace(self.data_path, backup_path) # 즉각적 격리 및 초기 상태 회귀
    ```

### 2. 아토믹 쓰기 (Atomic Write) - 데이터 영속성 보장
- **[개념]**: 저장 프로세스 도중 발생할 수 있는 데이터 손상을 방지하기 위해 '파일 교체' 방식을 채택함.
- **[구현 코드]**: 
    ```python
    tmp_path = self.data_path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(save_data, f)
    os.replace(tmp_path, self.data_path) # 운영체제 수준의 원자적 이름 변경(Rename) 활용
    ```

---

## Ⅲ. 파일별 상세 기술 명세 (Technical Deep-Dive)

### 1. quiz.py (Data Model)
- **캡슐화**: 퀴즈 데이터의 내부 속성을 보호하며, `to_dict` / `from_dict`를 통해 JSON 데이터와 상호 변환(직렬화/역직렬화)함.

### 2. utils.py (Input Validation)
- **데이터 정제**: 부적절한 사용자 입력으로부터 시스템 로직을 보호하며, 예외 상황을 최상위 계층으로 전계(Propagate)함.

### 3. game.py (Core Business Logic)
- **경로 최적화**: `quiz-game/state.json`으로 물리적 경로를 지정하여, 실행 환경에 따른 데이터 분산 문제 해결.
- **초기 데이터 주입 (Self-Seeding)**: 데이터 파일 부재 시, 내장된 기본 퀴즈 세트를 자동으로 로드하여 즉각적인 실행 환경 제공.

### 4. main.py (Global Exception Handler)
- **입력 렌더링 최적화**: `readline` 모듈 도입으로 한글 입력 시 발생하는 커서 위치 불일치 및 렌더링 버그 해결.
- **예외 처리 구조 (Global Error Handling)**:
    - **[설계 의도]**: 비정상 종료 상황에서도 메모리 내 데이터를 손실 없이 저장소에 기록함.
    - **[구현 코드]**: 
    ```python
    # 전체 게임 실행 루프
    except (KeyboardInterrupt, EOFError):
        print("\n[비상] 비정상 종료 감지! 데이터를 긴급 저장하고 종료함.")
        app.save_state() # 런타임 데이터를 파일 시스템으로 긴급 동기화
    ```

---

## Ⅳ. 설계의 확장성 (Scalability)
현 시스템은 **관심사 분리(SoC)**가 완료되어 있어, 향후 다음과 같은 업그레이드를 수용할 수 있음:
1. **인터페이스**: UI 계층만 수정하여 GUI나 Web 환경으로 확장 가능.
2. **저장소**: 추상화된 로드/저장 메서드를 통해 SQLite 등 데이터베이스로 전환 용이.

---

## Ⅴ. Git 작업 마스터 플랜 (14단계 완료)
- `Feat`: 기능 추가, `Fix`: 버그 수정, `Docs`: README 등 문서화, `Chore`: 세팅, `Refactor`: 구조 개선 컨벤션 준수 완료함.

| STEP | 커밋 내용 (Summary) |
|---|---|
| 1 | quiz-game 폴더 초기 구조 세팅 |
| 2 | Quiz 클래스 완성 (캡슐화, JSON 직렬화) |
| 3 | utils.py 입력 필터링 및 예외 전결 구현 |
| 4 | QuizGame 클래스 정의 및 JSON 방어 로직 |
| ... | ... (기능 개발 및 병합 완료) ... |
| 14 | 프로젝트 README 및 최종 명세서 완성 |

---

## Ⅵ. 요약 및 정리
1. **플레이 기준**: 모든 문제 진행을 1개의 플레이로 규정하되, '포기(5번)'는 정상 종료로 간주하여 점수를 합산함.
2. **점수 집계**: 실시간 RAM 스코어링 후 최종 결산소에서 최고 점수 비교 갱신 작업을 수행함.
3. **무결성 사수**: 비정상 강격 탈출 시에도 `main.py`에 설치된 최상위 예외 처리기가 작동하여 데이터를 안전하게 저장함.
