"""
B3-2 AI Git Generator - CLI 인자 파서 및 옵션 라우팅 모듈
설계 목적: argparse 기반으로 commit/pr 서브커맨드와 --model, --temperature, --max-tokens, --safe-mode 옵션을 파싱함.
유연성: -safe-mode 및 --safe-mode, 축약형(-m, -t, -s) 옵션을 모두 호환함.
주석 규격: 명사형 및 개조식(~함, ~임, ~를 위한) 준수함.
"""
import argparse
import sys
from typing import List, Optional


class CLIParser:
    """
    명령줄 인자를 파싱하고 검증하는 CLI 파서 클래스임.
    """

    def __init__(self) -> None:
        """인자 파서를 초기화하고 서브커맨드 및 옵션을 구성함."""
        self.parser = argparse.ArgumentParser(
            prog="ai-gitgen",
            description="AI 기반 Git 변경 사항(diff/status) 커밋 메시지 및 PR 설명 자동 생성 도구"
        )
        self._setup_arguments()

    def _setup_arguments(self) -> None:
        """서브커맨드 및 공통 옵션을 등록함."""
        subparsers = self.parser.add_subparsers(
            dest="command",
            help="실행할 자동 생성 작업 (commit 또는 pr)"
        )

        # 1. commit 서브커맨드임
        commit_parser = subparsers.add_parser("commit", help="Git 변경 사항 기반 커밋 메시지 자동 생성")
        self._add_common_options(commit_parser)

        # 2. pr 서브커맨드임
        pr_parser = subparsers.add_parser("pr", help="Git 변경 사항 기반 Pull Request 제목 및 본문 초안 자동 생성")
        self._add_common_options(pr_parser)

    def _add_common_options(self, target_parser: argparse.ArgumentParser) -> None:
        """공통 AI 및 보안 옵션을 추가함."""
        target_parser.add_argument(
            "-m", "--model",
            default="gemini-1.5-flash",
            help="사용할 AI 모델명 (기본값: gemini-1.5-flash)"
        )
        target_parser.add_argument(
            "-t", "--temperature",
            type=float,
            default=0.2,
            help="생성 온도 (결정론적 규격을 위해 기본값: 0.2)"
        )
        target_parser.add_argument(
            "--max-tokens",
            type=int,
            default=1000,
            help="최대 생성 토큰 수 (기본값: 1000)"
        )
        target_parser.add_argument(
            "--safe-mode", "-safe-mode", "-s",
            action="store_true",
            dest="safe_mode",
            help="안전 모드 활성화 (민감 정보 정규식 마스킹 및 diff 200줄 절삭)"
        )

    def parse_args(self, args: Optional[List[str]] = None) -> argparse.Namespace:
        """
        인자 목록을 파싱하여 반환함.
        명령어가 누락된 경우 도움말을 출력함.
        """
        # 단일 하이픈 -safe-mode 처리를 위한 인자 정규화임
        raw_args = list(args if args is not None else sys.argv[1:])
        normalized_args: List[str] = []
        for arg in raw_args:
            if arg == "-safe-mode":
                normalized_args.append("--safe-mode")
            elif arg == "-model":
                normalized_args.append("--model")
            elif arg == "-temperature":
                normalized_args.append("--temperature")
            elif arg == "-max-tokens":
                normalized_args.append("--max-tokens")
            else:
                normalized_args.append(arg)

        parsed = self.parser.parse_args(normalized_args)
        return parsed
