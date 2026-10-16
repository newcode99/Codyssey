"""
B5-2 Mini Git - CLI REPL 및 명령 라우터 모듈
설계 목적: 사용자의 터미널 입력을 shlex 기반으로 안전하게 토큰화하고,
대소문자 무구분 명령 정규화 및 Traceback 완전 차단을 수행함.
"""
import shlex
import sys
from typing import List
from mini_git import MiniGit


class MiniGitCLI:
    """
    Mini Git의 REPL(Read-Eval-Print Loop) 대화형 인터페이스를 제공하는 클래스임.
    """

    def __init__(self, engine: MiniGit = None) -> None:
        """
        CLI 엔진을 초기화함.
        인자로 주어진 엔진이 없을 경우 신규 MiniGit 인스턴스를 생성함.
        """
        self.engine: MiniGit = engine if engine is not None else MiniGit()

    def execute_line(self, raw_line: str) -> str:
        """
        한 줄의 입력 명령 문자열을 파싱하고 적절한 엔진 메서드로 라우팅함.
        따옴표로 감싸진 공백을 온전히 보존하며 파이썬 예외를 안전하게 캡슐화함.
        """
        trimmed = raw_line.strip()
        if not trimmed:
            return ""

        # 1. shlex를 활용한 인자 토큰 분리임 (따옴표 내부 공백 보존)
        try:
            tokens: List[str] = shlex.split(trimmed)
        except ValueError as err:
            return f"(error) Invalid args: {err}"

        if not tokens:
            return ""

        command = tokens[0].upper()
        args = tokens[1:]

        # 2. 명령어 분기 및 라우팅임
        try:
            if command == "INIT":
                if len(args) != 1:
                    return "(error) Invalid args"
                return self.engine.init(args[0])

            elif command == "BRANCH":
                if len(args) != 1:
                    return "(error) Invalid args"
                return self.engine.branch(args[0])

            elif command == "SWITCH":
                if len(args) != 1:
                    return "(error) Invalid args"
                return self.engine.switch(args[0])

            elif command == "COMMIT":
                if len(args) != 1:
                    return "(error) Invalid args"
                return self.engine.commit(args[0])

            elif command == "LOG":
                sort_by = None
                if len(args) == 1:
                    arg = args[0]
                    if arg.startswith("--sort-by="):
                        sort_by = arg.split("=", 1)[1].lower()
                    else:
                        return f"(error) Invalid args: {arg}"
                elif len(args) > 1:
                    return "(error) Invalid args"
                return self.engine.log(sort_by=sort_by)

            elif command == "PATH":
                if len(args) != 2:
                    return "(error) Invalid args"
                return self.engine.path(args[0], args[1])

            elif command == "ANCESTORS":
                if len(args) != 1:
                    return "(error) Invalid args"
                return self.engine.ancestors(args[0])

            elif command == "SEARCH":
                if len(args) != 1:
                    return "(error) Invalid args"
                arg = args[0]
                if arg.startswith("--author="):
                    author_query = arg.split("=", 1)[1]
                    return self.engine.search(author_query, is_author=True)
                else:
                    return self.engine.search(arg, is_author=False)

            else:
                return f"(error) Unknown command: {tokens[0]}"

        except Exception as err:
            # 예기치 않은 시스템 예외에 대해 Traceback 노출을 원천 방어함
            return f"(error) Internal error: {err}"

    def run_repl(self) -> None:
        """
        터미널에서 사용자와 대화식으로 통신하는 대화형 REPL 루프임.
        'exit' 또는 'quit' 입력 시 정상 종료함.
        """
        prompt = "mini-git> "
        while True:
            try:
                line = input(prompt)
            except (EOFError, KeyboardInterrupt):
                print()
                break

            stripped = line.strip()
            if not stripped:
                continue

            # 종료 명령어 판별임
            if stripped.lower() in ("exit", "quit"):
                break

            response = self.execute_line(stripped)
            if response:
                print(response)
