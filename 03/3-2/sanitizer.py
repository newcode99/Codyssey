"""
B3-2 AI Git Generator - 보안 마스킹 및 전송량 제어 모듈
설계 목적: safe-mode 옵션 활성화 시 diff 내 민감 정보(API Key, 비밀번호, 이메일 등)를 정규식으로 마스킹하고,
과도한 토큰 비용 방지를 위해 diff 파일 수(최대 10개) 및 라인 수(최대 200줄)를 제한함.
주석 규격: 명사형 및 개조식(~함, ~임, ~를 위한) 준수함.
"""
import re
from typing import List, Tuple


class DataSanitizer:
    """
    diff 텍스트 내 민감 정보를 비식별화하고 전송량을 안전하게 제어하는 보안 클래스임.
    """

    def __init__(self, max_files: int = 10, max_lines: int = 200) -> None:
        """한도 파라미터 및 컴파일된 정규식 패턴을 초기화함."""
        self.max_files: int = max_files
        self.max_lines: int = max_lines

        # 1. API Key 및 토큰 정규식 패턴임 (OpenAI sk-, GitHub ghp-, Google AIza, Bearer 등)
        self.api_key_regex = re.compile(
            r"(sk-[a-zA-Z0-9]{20,}|ghp_[a-zA-Z0-9]{20,}|AIza[0-9A-Za-z-_]{35}|Bearer\s+[a-zA-Z0-9_\-\.]{20,})",
            re.IGNORECASE
        )

        # 2. 이메일 주소 정규식 패턴임
        self.email_regex = re.compile(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        )

        # 3. 비밀번호 및 시크릿 변수 할당문 정규식 패턴임 (이미 마스킹된 [REDACTED_*]는 제외함)
        self.secret_assign_regex = re.compile(
            r"((?:password|passwd|secret|api_key|token|auth)\s*[:=]\s*['\"])(?!\s*\[REDACTED_)([^'\"]+)(['\"])",
            re.IGNORECASE
        )

        # 4. IPv4 주소 정규식 패턴임
        self.ip_regex = re.compile(
            r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b"
        )

    def mask_sensitive_patterns(self, text: str) -> str:
        """
        텍스트 내 민감한 패턴을 식별하여 안전한 대체 문자열로 치환함.
        치환 대상: API 키, 이메일, 패스워드 할당값, IP 주소임.
        """
        # API 키 마스킹임
        text = self.api_key_regex.sub("[REDACTED_API_KEY]", text)

        # 이메일 주소 마스킹임
        text = self.email_regex.sub("[REDACTED_EMAIL]", text)

        # 비밀번호 할당값 마스킹임
        text = self.secret_assign_regex.sub(r"\1[REDACTED_SECRET]\3", text)

        # IP 주소 마스킹임
        text = self.ip_regex.sub("[REDACTED_IP]", text)

        return text

    def truncate_diff(self, diff_text: str) -> Tuple[str, bool]:
        """
        diff 텍스트의 라인 수가 설정된 최대 한도(max_lines)를 초과할 경우 잘라냄.
        반환값: (정제된_diff, 절삭_발생_여부)
        """
        lines = diff_text.splitlines()
        if len(lines) <= self.max_lines:
            return diff_text, False

        truncated_lines = lines[:self.max_lines]
        truncated_lines.append(f"\n[... Diff truncated: {len(lines) - self.max_lines} lines omitted for safe mode ...]")
        return "\n".join(truncated_lines), True

    def filter_file_list(self, files: List[str]) -> Tuple[List[str], bool]:
        """
        파일 목록이 설정된 최대 파일 수(max_files)를 초과할 경우 목록을 절삭함.
        반환값: (정제된_파일목록, 절삭_발생_여부)
        """
        if len(files) <= self.max_files:
            return files, False

        truncated_files = files[:self.max_files]
        truncated_files.append(f"[... and {len(files) - self.max_files} more files omitted for safe mode ...]")
        return truncated_files, True

    def sanitize(self, files: List[str], diff_text: str, safe_mode: bool) -> Tuple[List[str], str, bool]:
        """
        safe_mode 옵션에 따라 마스킹과 절삭을 통합 수행함.
        safe_mode가 비활성화된 경우에도 최소한의 안전 한도(1000줄)는 적용함.
        반환값: (sanitized_files, sanitized_diff, was_truncated)
        """
        if not safe_mode:
            # safe-mode OFF 상태라도 메모리 보호를 위한 기본 1000줄 제한 적용임
            lines = diff_text.splitlines()
            if len(lines) > 1000:
                diff_text = "\n".join(lines[:1000]) + "\n[... Diff truncated at 1000 lines ...]"
                return files, diff_text, True
            return files, diff_text, False

        # safe-mode ON 상태: 엄격한 정규식 마스킹 및 10개 파일 / 200줄 절삭 적용임
        masked_diff = self.mask_sensitive_patterns(diff_text)
        sanitized_diff, diff_truncated = self.truncate_diff(masked_diff)
        sanitized_files, files_truncated = self.filter_file_list(files)

        was_truncated = diff_truncated or files_truncated
        return sanitized_files, sanitized_diff, was_truncated
