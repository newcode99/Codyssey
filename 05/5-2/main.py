"""
B5-2 Mini Git - 공식 엔트리포인트 실행 모듈
설계 목적: 과제 명세 7번 제약사항('실행 커맨드: python main.py')을 충족하며,
CLI REPL 환경을 기동하는 진입점 역할을 수행함.
"""
import sys
from cli import MiniGitCLI


def main() -> None:
    """
    Mini Git CLI 애플리케이션의 메인 진입점 함수임.
    REPL 루프를 시작하고 정상 종료 시 0을 반환함.
    """
    cli = MiniGitCLI()
    cli.run_repl()


if __name__ == "__main__":
    main()
