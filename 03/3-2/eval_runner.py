"""
B3-2 AI Git Generator - 평가자 전용 대화형 메뉴 러너 모듈
설계 목적: 평가자 또는 사용자가 번호만 누르면 5대 핵심 시나리오를 즉시 실행하고 결과를 실시간으로 확인할 수 있도록 지원함.
주석 규격: 명사형 및 개조식(~함, ~임, ~를 위한) 준수함.
"""
import os
import subprocess
import sys


def print_banner() -> None:
    """메인 평가 배너를 출력함."""
    print("=" * 70)
    print("   B3-2 AI Git Generator 기술 평가 및 대화형 시연 러너")
    print("=" * 70)
    print("1. [검증] AST 정적 분석기 및 10대 자동화 테스트 스위트 실행")
    print("2. [시나리오 1] 변경 사항 부재 시 조기 종료 검증 (commit)")
    print("3. [시나리오 2] Git 변경 사항 기반 커밋 메시지 자동 생성 (commit)")
    print("4. [시나리오 3] Git 변경 사항 기반 PR 제목 및 본문 자동 생성 (pr)")
    print("5. [시나리오 4] safe-mode 민감정보 마스킹 및 diff 전송 한도 검증")
    print("6. [통합] 1~5번 시나리오 전체 연속 실행")
    print("0. 종료 (Exit)")
    print("=" * 70)


def run_command(cmd: str) -> None:
    """주어진 터미널 명령어를 실행하고 결과를 출력함."""
    print(f"\n[실행 명령어] -> {cmd}")
    print("-" * 70)
    result = subprocess.run(cmd, shell=True)
    print("-" * 70)
    if result.returncode == 0:
        print("[결과] 성공 (Exit Code: 0)\n")
    else:
        print(f"[결과] 오류 또는 조기 종료 (Exit Code: {result.returncode})\n")


def main() -> None:
    """대화형 메뉴 루프를 실행함."""
    curr_dir = os.path.dirname(os.path.abspath(__file__))

    while True:
        print_banner()
        choice = input("실행할 번호를 입력하세요 (0~6): ").strip()

        if choice == "0":
            print("\n평가 러너를 종료함.")
            break
        elif choice == "1":
            run_command(f"python3 {os.path.join(curr_dir, 'test_suite.py')}")
        elif choice == "2":
            run_command(f"python3 {os.path.join(curr_dir, 'main.py')} commit")
        elif choice == "3":
            run_command(f"python3 {os.path.join(curr_dir, 'main.py')} commit")
        elif choice == "4":
            run_command(f"python3 {os.path.join(curr_dir, 'main.py')} pr")
        elif choice == "5":
            run_command(f"python3 {os.path.join(curr_dir, 'main.py')} commit --safe-mode")
        elif choice == "6":
            print("\n>>> 전체 시나리오 일괄 연속 실행 시작 <<<\n")
            run_command(f"python3 {os.path.join(curr_dir, 'test_suite.py')}")
            run_command(f"python3 {os.path.join(curr_dir, 'main.py')} commit")
            run_command(f"python3 {os.path.join(curr_dir, 'main.py')} pr")
            run_command(f"python3 {os.path.join(curr_dir, 'main.py')} commit --safe-mode")
            print(">>> 전체 시나리오 실행 완료 <<<\n")
        else:
            print("\n올바른 번호를 선택하기 바람.\n")


if __name__ == "__main__":
    main()
