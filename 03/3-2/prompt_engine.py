"""
B3-2 AI Git Generator - 프롬프트 엔지니어링 모듈
설계 목적: Git 변경 내역(status, diff)을 기반으로 실무 표준 커밋 메시지와 PR 템플릿 초안을 생성하는 프롬프트를 빌드함.
핵심 규칙 강제: 커밋 제목(50자 권장, 최대 72자), PR 제목(최대 80자), Why/What/How to Test 필수 3대 섹션을 명시적으로 지시함.
주석 규격: 명사형 및 개조식(~함, ~임, ~를 위한) 준수함.
"""
from typing import List


class PromptEngine:
    """
    커밋 메시지 및 Pull Request 설명 생성을 위한 시스템 및 사용자 프롬프트를 구성하는 클래스임.
    """

    @staticmethod
    def build_commit_prompt(changed_files: List[str], diff_text: str) -> str:
        """
        커밋 메시지 전용 프롬프트를 빌드함.
        요구사항:
        1. 첫 줄은 제목(50자 이내 권장, 최대 72자, 관례적 접두사 feat/fix/docs/refactor 등 적용).
        2. 둘째 줄은 빈 줄.
        3. 셋째 줄부터 본문: 변경된 파일 1~3개 언급 및 핵심 변경 1~2개를 불릿('- ')으로 기술함.
        4. 인사말, 서두, 마크다운 코드블록 백틱(```) 출력 금지함.
        """
        file_list_str = "\n".join(f"- {f}" for f in changed_files[:10])
        prompt = f"""당신은 10년 차 시니어 소프트웨어 엔지니어이자 코드 리뷰어임.
제공된 Git 변경 파일 목록과 Diff 내용을 분석하여 실무 표준 규격의 Git 커밋 메시지를 작성해야 함.

[출력 형식 규칙 - 반드시 엄수할 것]
1. 첫 번째 줄(제목):
   - 반드시 1줄로 작성할 것.
   - 50자 이내 권장, 절대 72자를 초과하지 말 것.
   - 변경 성격에 맞는 conventional commit 접두사를 반드시 포함할 것 (예: feat:, fix:, refactor:, docs:, chore:).
2. 두 번째 줄:
   - 반드시 완전히 빈 줄(Empty line)로 둘 것.
3. 세 번째 줄 이후(본문):
   - 변경된 주요 파일/모듈(1~3개)을 언급할 것.
   - 핵심 변경 사항을 1~2개의 불릿('- ') 기호로 간결하게 요약할 것.
4. 절대 금지 사항:
   - "Here is the commit message:" 같은 인사말이나 설명 문구를 일체 포함하지 말 것.
   - 텍스트 전체를 감싸는 마크다운 백틱(```) 기호를 절대 쓰지 말 것. 오직 커밋 메시지 텍스트 자체만 출력할 것.

[변경된 파일 목록]
{file_list_str}

[Git Diff 내용]
{diff_text}
"""
        return prompt.strip()

    @staticmethod
    def build_pr_prompt(changed_files: List[str], diff_text: str, current_branch: str) -> str:
        """
        Pull Request(PR) 설명 전용 프롬프트를 빌드함.
        요구사항:
        1. 첫 줄: 'Title: <PR 제목>' (최대 80자 이내 1줄).
        2. 둘째 줄: 빈 줄.
        3. 셋째 줄 이후: 본문 템플릿(## Why, ## What, ## How to Test) 3대 섹션 필수 및 각 섹션 최소 1개 이상 불릿('- ').
        4. 인사말, 잡담, 마크다운 코드블록 백틱(```) 출력 금지함.
        """
        file_list_str = "\n".join(f"- {f}" for f in changed_files[:10])
        prompt = f"""당신은 10년 차 시니어 소프트웨어 엔지니어이자 오픈소스 메인테이너임.
제공된 브랜치 정보, 변경 파일 목록, Diff 내용을 분석하여 GitHub Pull Request(PR) 제목과 본문 초안을 작성해야 함.

[출력 형식 규칙 - 반드시 엄수할 것]
1. 첫 번째 줄:
   - 반드시 'Title: <제목>' 형식으로 1줄로 작성할 것.
   - PR 제목은 최대 80자를 초과하지 말 것.
   - 변경 내용의 핵심을 명확히 요약할 것.
2. 두 번째 줄:
   - 반드시 빈 줄(Empty line)로 둘 것.
3. 세 번째 줄 이후(본문 템플릿):
   - 반드시 아래 3개 섹션 헤더를 정확한 명칭으로 포함할 것:
     ## Why
     - (변경 배경 및 필요성을 1개 이상의 불릿으로 작성)
     ## What
     - (핵심 변경 사항과 추가/수정된 기능을 1개 이상의 불릿으로 작성)
     ## How to Test
     - (동작 확인 및 검증 방법을 1개 이상의 불릿으로 작성)
   - 각 섹션에는 반드시 최소 1개 이상의 불릿('- ')을 포함할 것.
4. 절대 금지 사항:
   - "다음은 PR 초안입니다" 같은 불필요한 메타 발언을 일체 포함하지 말 것.
   - 전체를 감싸는 마크다운 백틱(```) 기호를 절대 쓰지 말 것.

[현재 활성 브랜치]
{current_branch}

[변경된 파일 목록]
{file_list_str}

[Git Diff 내용]
{diff_text}
"""
        return prompt.strip()
