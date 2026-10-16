"""
B5-2 Mini Git - 대화형 기능 평가 및 시나리오 자동 실행기
설계 목적: 분리된 커맨드 파일들을 파싱하여 Mini Git의 각 기능을 즉각 실행하고,
입력과 출력 결과를 터미널에 직관적으로 렌더링하여 평가를 용이하게 함.
제약 준수: 파이썬 표준 정렬 API 및 외부 라이브러리 일체 배제, 주석 개조식 규격 준수함.
"""
import os
import sys
from cli import MiniGitCLI


COMMANDS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "commands")


def run_command_file(file_path: str, scenario_title: str) -> None:
    """
    지정된 텍스트 파일의 명령어 목록을 순차적으로 실행하고 결과를 출력함.
    file_path: 실행할 명령어 목록이 저장된 텍스트 파일 경로임.
    scenario_title: 평가 시나리오의 제목임.
    """
    print("\n" + "=" * 70)
    print(f"▶ [시나리오 평가] {scenario_title}")
    print(f"▶ 대상 파일: {os.path.basename(file_path)}")
    print("=" * 70)

    if not os.path.exists(file_path):
        print(f"❌ 파일을 찾을 수 없음: {file_path}")
        return

    cli = MiniGitCLI()

    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for idx, raw_line in enumerate(lines, 1):
        cmd_line = raw_line.strip()
        if not cmd_line or cmd_line.startswith("#"):
            continue

        print(f"\n[Step {idx:02d}] mini-git> {cmd_line}")
        if cmd_line.lower() in ("exit", "quit"):
            print("→ 세션 종료됨.")
            break

        output = cli.execute_line(cmd_line)
        if output:
            print(output)
        else:
            print("(출력 없음)")

    print("\n" + "-" * 70)
    print(f"✔ [시나리오 완료] {scenario_title} 실행 종료")
    print("-" * 70)


def show_menu() -> None:
    """대화형 평가 메뉴를 화면에 출력함."""
    print("\n" + "=" * 60)
    print("      🌟 B5-2 Mini Git 기능별 즉시 평가 러너 🌟")
    print("=" * 60)
    print("1. [공식 시나리오] 과제 8번 실행 예시 시나리오 검증")
    print("2. [브랜치 & 위상정렬] 다중 브랜치 분기 및 인과 순서 검증")
    print("3. [역색인 & 커스텀 정렬] O(1) 검색 및 date/author 정렬 비교")
    print("4. [예외 & 엣지케이스] 미초기화, 미존재 객체 에러 방어 검증")
    print("5. [전체 일괄 실행] 1~4번 시나리오 연속 자동 평가")
    print("6. [종합 테스트 스위트] AST 정적 분석 및 10대 검증 (test_suite.py)")
    print("0. 종료")
    print("=" * 60)


def main() -> None:
    """평가 러너의 진입점 루프임."""
    # CLI 인자로 --all이 전달된 경우 비대화형으로 전체 실행함
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        run_command_file(os.path.join(COMMANDS_DIR, "01_official_demo.txt"), "공식 실행 예시 시나리오")
        run_command_file(os.path.join(COMMANDS_DIR, "02_branch_divergence_and_path.txt"), "브랜치 분기 및 위상 정렬")
        run_command_file(os.path.join(COMMANDS_DIR, "03_search_and_sorting.txt"), "역색인 검색 및 정렬")
        run_command_file(os.path.join(COMMANDS_DIR, "04_ancestors_and_edge_cases.txt"), "에러 방어 및 엣지 케이스")
        return

    while True:
        show_menu()
        try:
            choice = input("실행할 번호를 입력하세요 (0-6): ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n프로그램을 종료함.")
            break

        if choice == "0":
            print("평가 러너를 종료함.")
            break
        elif choice == "1":
            run_command_file(os.path.join(COMMANDS_DIR, "01_official_demo.txt"), "과제 8번 공식 실행 예시")
        elif choice == "2":
            run_command_file(os.path.join(COMMANDS_DIR, "02_branch_divergence_and_path.txt"), "브랜치 분기 및 위상 정렬")
        elif choice == "3":
            run_command_file(os.path.join(COMMANDS_DIR, "03_search_and_sorting.txt"), "역색인 검색 및 정렬")
        elif choice == "4":
            run_command_file(os.path.join(COMMANDS_DIR, "04_ancestors_and_edge_cases.txt"), "에러 방어 및 엣지 케이스")
        elif choice == "5":
            run_command_file(os.path.join(COMMANDS_DIR, "01_official_demo.txt"), "공식 실행 예시")
            run_command_file(os.path.join(COMMANDS_DIR, "02_branch_divergence_and_path.txt"), "브랜치 분기 및 위상 정렬")
            run_command_file(os.path.join(COMMANDS_DIR, "03_search_and_sorting.txt"), "역색인 검색 및 정렬")
            run_command_file(os.path.join(COMMANDS_DIR, "04_ancestors_and_edge_cases.txt"), "에러 방어 및 엣지 케이스")
        elif choice == "6":
            import test_suite
            test_suite.main()
        else:
            print("⚠ 올바른 번호를 입력해주시기 바람 (0-6).")


if __name__ == "__main__":
    main()
