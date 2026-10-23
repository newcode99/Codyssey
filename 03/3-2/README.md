# B3-2 AI 기반 Git 커밋 및 PR 자동 생성 CLI (ai-gitgen)

AI API 연동의 핵심인 **'입력 컨텍스트 설계'**와 **'결과물 품질 제어'**를 체득하기 위한 Git 자동화 CLI 도구입니다.  
`git diff`와 `git status` 결과를 수집하여, 실무 표준 규격을 만족하는 **커밋 메시지**와 **Pull Request(PR) 설명 초안**을 단일 터미널 명령으로 자동 생성합니다.

---

## 🌟 핵심 기능 및 특징

1. **Zero-Dependency 초경량 REST 클라이언트**:
   - 무거운 외부 SDK(`openai`, `google-generativeai`) 설치 없이 Python 표준 라이브러리(`urllib`)만으로 동작하여 1초 만에 즉시 실행됩니다.
2. **실무 표준 커밋 메시지 자동 생성 (`commit`)**:
   - 커밋 제목 1줄(50자 이내 권장, 최대 72자) 및 Conventional Commit 접두사(`feat:`, `fix:` 등) 적용.
   - 변경된 주요 파일(1~3개) 및 핵심 변경 사항 불릿('- ') 요약 본문 제공.
3. **템플릿 구조화 PR 초안 자동 생성 (`pr`)**:
   - PR 제목 1줄(최대 80자) 및 필수 3대 섹션(`## Why`, `## What`, `## How to Test`)과 섹션별 불릿 본문 완비.
4. **안전 모드 (`--safe-mode`) 탑재**:
   - API Key, 비밀번호, 이메일, IP 주소 등 민감 정보를 정규식으로 감지하여 `[REDACTED_*]`로 자동 마스킹.
   - Diff 전송량을 최대 10개 파일, 200줄로 제한하여 토큰 비용 폭발을 물리적으로 차단.
5. **결정론적 가드레일 후처리 (Post-Processing)**:
   - AI 응답의 마크다운 백틱(```) 제거, 제목 길이 초과 절삭, 누락된 PR 섹션 템플릿 복원을 비용 0원으로 즉시 수행.
6. **Traceback 0% 에러 캡슐화**:
   - API Key 누락, 네트워크 단절, 비-Git 디렉토리 실행 등 모든 예외 상황에서 파이썬 에러 로그 노출을 차단하고 친절한 안내 메시지만 출력.

---

## 🚀 설치 및 환경 설정

### 1. 요구 환경
* Python 3.10 이상
* Git 2.20 이상

### 2. 저장소 클론 및 디렉토리 이동
```bash
git clone https://github.com/newcode99/Codyssey.git
cd Codyssey/03/3-2   # 또는 해당 프로젝트 루트 디렉토리
```

### 3. API Key 환경변수 설정
AI API Key는 보안을 위해 코드에 하드코딩하지 않고 환경변수로만 관리합니다:

```bash
# Google Gemini API Key 설정 시 (기본 권장)
export AI_API_KEY="AIzaSy..."

# OpenAI 호환 API Key 사용 시 (선택 사항)
export AI_API_KEY="sk-..."
export AI_API_ENDPOINT="https://api.openai.com/v1/chat/completions"
```

---

## 💻 사용 방법 및 실행 예시

### 1. 커밋 메시지 자동 생성 (`commit`)
Git 변경 사항을 분석하여 복사 가능한 커밋 메시지를 생성합니다.

```bash
python3 main.py commit
```

**[터미널 출력 예시]**
```text
[INFO] Git status 수집 완료: 2개 파일 변경 감지
[INFO] Git diff 수집 완료: 45줄
[INFO] AI API 요청 중...
[DONE] 커밋 메시지 생성 완료 (AI 호출: 1회)
------------------------ Commit Message ------------------------
feat: add user authentication and password validation

- auth_service.py: Implemented verify_password function with hash checking.
- user_model.py: Added password_hash field to User entity.
----------------------------------------------------------------
```

---

### 2. Pull Request(PR) 초안 자동 생성 (`pr`)
브랜치 정보와 diff를 분석하여 GitHub PR 템플릿 초안을 생성합니다.

```bash
python3 main.py pr
```

**[터미널 출력 예시]**
```text
[INFO] 현재 브랜치: feature/auth-system
[INFO] Git status 수집 완료: 2개 파일 변경 감지
[INFO] Git diff 수집 완료: 45줄
[INFO] AI API 요청 중...
[DONE] PR 초안 생성 완료 (AI 호출: 1회)
--------------------------- PR Title ---------------------------
feat: implement secure user authentication service
--------------------------- PR Body ----------------------------
## Why
- 사용자 로그인 시 안전한 패스워드 검증 및 세션 관리가 필요함.
- 보안 감사를 충족하기 위한 해시 기반 인증 체계 도입 목적임.

## What
- auth_service.py에 verify_password 함수 신규 구현
- user_model.py에 password_hash 필드 추가 및 직렬화 반영

## How to Test
- python3 -m unittest discover tests 실행하여 인증 단위 테스트 검증
- 잘못된 비밀번호 입력 시 401 Unauthorized 반환 여부 확인
----------------------------------------------------------------
```

---

### 3. 안전 모드 활성화 (`--safe-mode`)
민감 정보가 포함되어 있을 가능성이 있는 경우 `--safe-mode`를 활성화합니다.

```bash
python3 main.py commit --safe-mode
```

**[터미널 출력 예시]**
```text
[INFO] Git status 수집 완료: 1개 파일 변경 감지
[INFO] Git diff 수집 완료: 320줄
[INFO] safe-mode 적용: 민감 정보 마스킹 및 diff 전송 한도(200줄/10파일) 제어 완료
[INFO] AI API 요청 중...
[DONE] 커밋 메시지 생성 완료 (AI 호출: 1회)
------------------------ Commit Message ------------------------
...
----------------------------------------------------------------
```

---

### 4. 파라미터 옵션 커스터마이징
모델, 생성 온도, 토큰 제한을 자유롭게 변경할 수 있습니다:

```bash
python3 main.py commit --model gemini-1.5-flash --temperature 0.1 --max-tokens 500
```

---

## 🛡️ 운영 및 비용 가이드

1. **민감 정보 포함 가능성과 대응 (Security Best Practices)**:
   - 커밋 대상 코드에 API Key, 개인정보, 데이터베이스 패스워드가 포함되지 않도록 커밋 전 검토가 권장됩니다.
   - 의심스러운 경우 항상 `--safe-mode` 옵션을 활성화하여 정규식 비식별화(`[REDACTED_*]`) 및 200줄 절삭을 적용하세요.
2. **비용 및 요청 횟수 제어 정책 (Cost & Quota Policy)**:
   - 본 도구는 과도한 API 비용 발생을 방지하기 위해 **1회 실행당 AI API 호출을 정확히 1회로 제한**합니다.
   - 생성 결과는 최종 정답이 아닌 '초안'이므로, 터미널에 출력된 내용을 검토한 뒤 복사하여 적용하는 워크플로우를 권장합니다.

---

## 🧪 자동화 검증 및 테스트 러너 실행

```bash
# AST 정적 분석 및 10대 자동화 테스트 스위트 실행
python3 test_suite.py

# 대화형 평가 러너 실행 (메뉴 번호 선택식)
python3 eval_runner.py
```
