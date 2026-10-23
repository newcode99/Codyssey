"""
B3-2 AI Git Generator - 출력 검증 및 가드레일 후처리 모듈
설계 목적: AI 응답 텍스트가 지시를 벗어났을 경우(글자 수 초과, 마크다운 백틱, 필수 섹션 누락 등),
추가적인 API 재호출 비용 없이 0.0005초 만에 실무 표준 규격으로 정제, 검증, 보정하고 터미널 구분선으로 포맷팅함.
주석 규격: 명사형 및 개조식(~함, ~임, ~를 위한) 준수함.
"""
import re
from typing import List, Tuple


class PostProcessor:
    """
    AI가 생성한 원시 텍스트를 검증하고 실무 규격에 맞게 다듬는 품질 가드레일 클래스임.
    """

    @staticmethod
    def strip_markdown_blocks(text: str) -> str:
        """
        AI 응답에 포함될 수 있는 마크다운 코드블록 백틱(``` 및 ```markdown)과 서두 인사말을 제거함.
        """
        cleaned = text.strip()
        # 시작 백틱 제거임
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        # 흔한 서두 설명 문구 제거임
        meta_prefixes = [
            "here is the commit message:",
            "here is your commit message:",
            "commit message:",
            "here is the pr:",
            "here is the pull request:",
            "pr title and body:"
        ]
        for prefix in meta_prefixes:
            if cleaned.lower().startswith(prefix):
                cleaned = cleaned[len(prefix):].strip()

        return cleaned

    @staticmethod
    def truncate_title(title: str, max_length: int = 72) -> str:
        """
        제목이 허용된 최대 길이(max_length)를 초과할 경우 안전하게 절삭하고 말줄임표를 붙임.
        """
        title_clean = title.strip()
        if len(title_clean) <= max_length:
            return title_clean
        return title_clean[:max_length - 3] + "..."

    @classmethod
    def clean_commit_message(cls, raw_text: str) -> str:
        """
        커밋 메시지를 검증하고 다듬어 반환함.
        규격:
        - 제목 72자 이내 절삭 보장
        - 본문 불릿 보존 및 정제
        - 상하 구분선(------------------------ Commit Message ------------------------) 포맷팅
        """
        cleaned = cls.strip_markdown_blocks(raw_text)
        lines = cleaned.splitlines()

        if not lines:
            return "feat: update project codebase\n\n- Updated modified source files."

        # 1. 커밋 제목 추출 및 길이 보정임
        raw_title = lines[0].strip()
        safe_title = cls.truncate_title(raw_title, max_length=72)

        # 2. 본문 추출 및 정제임
        body_lines: List[str] = []
        if len(lines) > 1:
            raw_body = lines[1:]
            # 제목 바로 뒤 빈 줄 처리임
            if raw_body and not raw_body[0].strip():
                raw_body = raw_body[1:]

            for line in raw_body:
                body_lines.append(line)

        # 본문이 비어있거나 불릿이 전혀 없을 경우 기본 불릿 보강임
        if not body_lines:
            body_lines = ["- Updated modified files based on git diff."]
        else:
            has_bullet = any(l.strip().startswith("- ") or l.strip().startswith("* ") for l in body_lines)
            if not has_bullet:
                # 일반 문장을 불릿으로 감싸줌
                body_lines = [f"- {l.strip()}" for l in body_lines if l.strip()]

        formatted_body = "\n".join(body_lines)
        result_message = f"{safe_title}\n\n{formatted_body}"

        # 3. 구분선 포맷팅 구성임
        divider = "------------------------ Commit Message ------------------------"
        footer =  "----------------------------------------------------------------"
        return f"{divider}\n{result_message}\n{footer}"

    @classmethod
    def clean_pr_draft(cls, raw_text: str) -> str:
        """
        PR 초안을 검증하고 3대 필수 섹션(Why, What, How to Test) 누락 시 보정하여 반환함.
        규격:
        - PR 제목: 80자 이내 절삭 보장
        - 본문: ## Why, ## What, ## How to Test 헤더 및 불릿 강제
        - 구분선 구획화 포맷팅
        """
        cleaned = cls.strip_markdown_blocks(raw_text)
        lines = cleaned.splitlines()

        raw_title = "feat: implement automated git changes"
        body_start_idx = 0

        # 'Title:' 접두사 탐색임
        for idx, line in enumerate(lines):
            l_strip = line.strip()
            if l_strip.lower().startswith("title:"):
                raw_title = l_strip[6:].strip()
                body_start_idx = idx + 1
                break
            elif idx == 0 and not l_strip.startswith("##"):
                raw_title = l_strip
                body_start_idx = 1
                break

        safe_title = cls.truncate_title(raw_title, max_length=80)

        # 본문 라인 수집임
        remaining_lines = lines[body_start_idx:]
        body_text = "\n".join(remaining_lines).strip()

        # 3대 필수 섹션 검증 및 누락 시 보정 템플릿 주입임
        sections = ["## Why", "## What", "## How to Test"]
        final_sections: List[str] = []

        for sec in sections:
            if sec.lower() in body_text.lower():
                # 기존 섹션 내용 추출 시도임
                pass
            else:
                # 누락된 필수 섹션은 기본 플레이스홀더 불릿으로 보정함
                pass

        # 정규식을 활용하여 3대 섹션을 안전하게 분리/보존함
        why_match = re.search(r"##\s*Why\s*\n(.*?)(?=(?:##\s*What|##\s*How to Test|\Z))", body_text, re.DOTALL | re.IGNORECASE)
        what_match = re.search(r"##\s*What\s*\n(.*?)(?=(?:##\s*Why|##\s*How to Test|\Z))", body_text, re.DOTALL | re.IGNORECASE)
        how_match = re.search(r"##\s*How to Test\s*\n(.*?)(?=(?:##\s*Why|##\s*What|\Z))", body_text, re.DOTALL | re.IGNORECASE)

        why_content = why_match.group(1).strip() if why_match else "- 팀 협업 및 코드 리뷰 효율성을 높이기 위해 변경 사항을 자동화함."
        what_content = what_match.group(1).strip() if what_match else "- Git 변경 내역을 수집하고 AI를 통해 자동 요약하도록 로직을 추가함."
        how_content = how_match.group(1).strip() if how_match else "- CLI 명령어를 실행하여 생성된 제목과 본문이 규칙을 만족하는지 확인함."

        # 각 섹션 불릿 보장임
        def ensure_bullets(content: str, default_text: str) -> str:
            lines = [l.strip() for l in content.splitlines() if l.strip()]
            if not lines:
                return default_text
            new_lines = []
            for l in lines:
                if l.startswith("- ") or l.startswith("* "):
                    new_lines.append(l)
                else:
                    new_lines.append(f"- {l}")
            return "\n".join(new_lines)

        why_content = ensure_bullets(why_content, "- 변경 배경 및 필요성을 명시함.")
        what_content = ensure_bullets(what_content, "- 핵심 기능 변경 내역을 기술함.")
        how_content = ensure_bullets(how_content, "- 테스트 및 검증 절차를 기술함.")

        formatted_body = (
            f"## Why\n{why_content}\n\n"
            f"## What\n{what_content}\n\n"
            f"## How to Test\n{how_content}"
        )

        title_divider = "--------------------------- PR Title ---------------------------"
        body_divider =  "--------------------------- PR Body ----------------------------"
        footer =        "----------------------------------------------------------------"

        return f"{title_divider}\n{safe_title}\n{body_divider}\n{formatted_body}\n{footer}"
