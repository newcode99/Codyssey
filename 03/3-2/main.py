"""
B3-2 AI Git Generator - 메인 파이프라인 오케스트레이터 및 진입점 모듈
설계 목적: Git 상태 수집 -> 보안 마스킹 -> 프롬프트 생성 -> AI REST 호출 -> 가드레일 후처리 -> 터미널 렌더링을 일원화함.
예외 안전성: Git 부재, API 키 미설정, 네트워크 단절 등 모든 예외를 캡슐화하여 Traceback 노출을 0%로 차단함.
주석 규격: 명사형 및 개조식(~함, ~임, ~를 위한) 준수함.
"""
import sys
from cli import CLIParser
from git_client import GitClient, GitClientError
from sanitizer import DataSanitizer
from prompt_engine import PromptEngine
from ai_client import AIClient, AIClientError
from post_processor import PostProcessor


def run_pipeline() -> int:
    """
    전체 자동 생성 파이프라인을 실행하는 메인 함수임.
    반환값: 정상 종료 시 0, 오류 발생 시 1임.
    """
    # 1. CLI 인자 파싱임
    parser = CLIParser()
    args = parser.parse_args()

    if not args.command:
        parser.parser.print_help()
        return 0

    command = args.command.lower()
    target_name = "커밋 메시지" if command == "commit" else "PR 초안"

    try:
        # 2. Git 변경 사항 수집임
        git_client = GitClient()
        files, diff, branch = git_client.collect_git_context()

        # 변경 사항 유무 검사임
        if not files and not diff.strip():
            print(f"[INFO] 변경 사항이 없습니다. {target_name}를 생성하지 않고 종료합니다.")
            return 0

        # PR 모드일 경우 현재 브랜치 로그 출력임
        if command == "pr":
            print(f"[INFO] 현재 브랜치: {branch}")

        diff_line_count = len(diff.splitlines())
        print(f"[INFO] Git status 수집 완료: {len(files)}개 파일 변경 감지")
        print(f"[INFO] Git diff 수집 완료: {diff_line_count}줄")

        # 3. 보안 마스킹 및 전송 한도 제어 (safe-mode)임
        sanitizer = DataSanitizer(max_files=10, max_lines=200)
        sanitized_files, sanitized_diff, was_truncated = sanitizer.sanitize(files, diff, safe_mode=args.safe_mode)

        if args.safe_mode:
            print("[INFO] safe-mode 적용: 민감 정보 마스킹 및 diff 전송 한도(200줄/10파일) 제어 완료")

        # 4. 프롬프트 생성임
        if command == "commit":
            prompt = PromptEngine.build_commit_prompt(sanitized_files, sanitized_diff)
        else:
            prompt = PromptEngine.build_pr_prompt(sanitized_files, sanitized_diff, branch)

        # 5. AI API 연동 및 텍스트 생성 (1회 호출 로깅)임
        ai_client = AIClient(
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens
        )

        print("[INFO] AI API 요청 중...")
        raw_response = ai_client.generate_text(prompt)
        print(f"[DONE] {target_name} 생성 완료 (AI 호출: {ai_client.call_count}회)")

        # 6. 출력 형식 검증 및 다듬기 (후처리 가드레일)임
        if command == "commit":
            final_output = PostProcessor.clean_commit_message(raw_response)
        else:
            final_output = PostProcessor.clean_pr_draft(raw_response)

        # 7. 최종 터미널 렌더링임
        print(final_output)
        return 0

    except GitClientError as git_err:
        print(f"[ERROR] {git_err}")
        return 1

    except AIClientError as ai_err:
        print(f"{ai_err}")
        return 1

    except Exception as unexpected_err:
        print(f"[ERROR] 실행 중 예상치 못한 오류 발생: {unexpected_err}")
        return 1


if __name__ == "__main__":
    sys.exit(run_pipeline())
