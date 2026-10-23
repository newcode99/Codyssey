"""
B3-2 AI Git Generator - Git 서브프로세스 클라이언트 모듈
설계 목적: 시스템 표준 git 명령어를 subprocess로 실행하여 변경 사항(status, diff)을 안전하게 수집함.
보안 및 안정성: 외부 GitPython 의존성 없이 순수 표준 라이브러리로 동작하며, 비-Git 환경을 사전에 차단함.
주석 규격: 명사형 및 개조식(~함, ~임, ~를 위한) 준수함.
"""
import os
import subprocess
from typing import List, Tuple


class GitClientError(Exception):
    """Git 클라이언트 도메인 전용 예외 클래스임."""
    pass


class GitClient:
    """
    로컬 Git 저장소의 상태와 변경 내역을 수집하는 핵심 클라이언트 클래스임.
    """

    def __init__(self, repo_path: str = ".") -> None:
        """저장소 작업 경로를 초기화하고 절대 경로로 정규화함."""
        self.repo_path: str = os.path.abspath(repo_path)

    def is_git_repository(self) -> bool:
        """
        현재 경로 또는 상위 경로에 .git 디렉토리가 존재하는지 검증함.
        정상 저장소일 경우 True, 아닐 경우 False를 반환함.
        """
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--is-inside-work-tree"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0 and result.stdout.strip() == "true"
        except FileNotFoundError:
            raise GitClientError("시스템에 git 명령어가 설치되어 있지 않거나 PATH에 없음.")

    def get_current_branch(self) -> str:
        """현재 활성화된 브랜치 이름을 조회하여 반환함."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode == 0:
                branch = result.stdout.strip()
                return branch if branch else "main"
            return "main"
        except Exception:
            return "main"

    def get_status_files(self) -> List[str]:
        """
        git status -s를 실행하여 변경된 파일 목록(Staged, Unstaged, Untracked)을 수집함.
        각 줄의 상태 기호를 정제하여 파일 경로 리스트를 반환함.
        """
        result = subprocess.run(
            ["git", "status", "-s"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            raise GitClientError(f"git status 수집 실패: {result.stderr.strip()}")

        files: List[str] = []
        for line in result.stdout.splitlines():
            line_str = line.strip()
            if not line_str:
                continue
            # 상태 기호(예: M, A, ??, D) 뒤의 파일 경로를 추출함
            parts = line_str.split(maxsplit=1)
            if len(parts) == 2:
                files.append(parts[1].strip())
            else:
                files.append(line_str)
        return files

    def get_diff(self) -> str:
        """
        Staged 변경 사항(cached)과 Unstaged 변경 사항을 모두 취합하여 diff 텍스트를 수집함.
        바이너리 파일은 제외하고 순수 텍스트 diff를 반환함.
        """
        # 1. Staged diff 수집임
        staged_result = subprocess.run(
            ["git", "diff", "--cached", "--no-color", "--ignore-space-at-eol"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        staged_diff = staged_result.stdout if staged_result.returncode == 0 else ""

        # 2. Unstaged diff 수집임
        unstaged_result = subprocess.run(
            ["git", "diff", "--no-color", "--ignore-space-at-eol"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            check=False
        )
        unstaged_diff = unstaged_result.stdout if unstaged_result.returncode == 0 else ""

        combined_diff = (staged_diff + "\n" + unstaged_diff).strip()
        return combined_diff

    def collect_git_context(self) -> Tuple[List[str], str, str]:
        """
        Git 루트 검증 후 변경 파일 목록, diff 텍스트, 현재 브랜치명을 통합 수집함.
        반환값: (changed_files, diff_text, current_branch)
        """
        if not self.is_git_repository():
            raise GitClientError("Git이 초기화된 프로젝트 루트 디렉토리(.git)가 아님.")

        branch = self.get_current_branch()
        files = self.get_status_files()
        diff = self.get_diff()

        return files, diff, branch
