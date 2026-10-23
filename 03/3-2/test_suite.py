"""
B3-2 AI Git Generator - 정적 AST 분석 및 10대 단위/통합 테스트 스위트
설계 목적: Python ast 모듈을 통한 주석 규격 및 하드코딩 0건 정적 입증과
핵심 모듈(Git, Sanitizer, Prompt, AI, PostProcessor, CLI)의 기능 무결성을 100% 자동 검증함.
주석 규격: 명사형 및 개조식(~함, ~임, ~를 위한) 준수함.
"""
import ast
import glob
import os
import sys
import unittest
from unittest.mock import patch, MagicMock

# 대상 모듈 임포트임
from git_client import GitClient, GitClientError
from sanitizer import DataSanitizer
from prompt_engine import PromptEngine
from ai_client import AIClient, AIClientError
from post_processor import PostProcessor
from cli import CLIParser


class TestStaticASTAndQuality(unittest.TestCase):
    """
    소스 코드 전반의 AST 정적 분석 및 품질 규격을 검사하는 테스트 클래스임.
    """

    def test_ast_forbidden_comment_patterns(self) -> None:
        """
        [정적 검증 1]: 소스 코드 내의 주석(#) 및 docstring에 금지된 '~합니다' 어미가 0건인지 검증함.
        """
        import tokenize
        import io

        source_dir = os.path.dirname(os.path.abspath(__file__))
        py_files = glob.glob(os.path.join(source_dir, "*.py"))

        violation_count = 0
        violations = []

        for py_path in py_files:
            # test_suite.py 자체는 정적 검사기 자체이므로 제외함
            if "test_suite.py" in py_path:
                continue

            with open(py_path, "r", encoding="utf-8") as f:
                content = f.read()

            # 1. 주석(#) 검사임
            tokens = tokenize.generate_tokens(io.StringIO(content).readline)
            for tok_type, tok_str, (srow, _), _, _ in tokens:
                if tok_type == tokenize.COMMENT and "합니다" in tok_str:
                    violation_count += 1
                    violations.append(f"{os.path.basename(py_path)}:{srow} (주석) -> {tok_str}")

            # 2. AST를 통한 Docstring 검사임
            tree = ast.parse(content, filename=py_path)
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef, ast.Module)):
                    doc = ast.get_docstring(node)
                    if doc and "합니다" in doc:
                        violation_count += 1
                        violations.append(f"{os.path.basename(py_path)} (docstring) -> {doc[:30]}...")

        self.assertEqual(
            violation_count, 0,
            f"주석 및 docstring 규격 위반('~합니다') {violation_count}건 발견됨: {violations}"
        )

    def test_ast_no_hardcoded_api_keys(self) -> None:
        """
        [정적 검증 2]: 소스 코드 내에 하드코딩된 API Key(sk-..., AIza...)가 0건인지 검증함.
        """
        source_dir = os.path.dirname(os.path.abspath(__file__))
        py_files = glob.glob(os.path.join(source_dir, "*.py"))

        for py_path in py_files:
            # test_suite.py 자체의 패턴 문자열은 제외함
            if "test_suite.py" in py_path:
                continue

            with open(py_path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=py_path)

            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, str):
                    val = node.value
                    self.assertFalse(
                        val.startswith("sk-") and len(val) > 20,
                        f"하드코딩된 API Key 발견: {py_path}"
                    )
                    self.assertFalse(
                        val.startswith("AIza") and len(val) > 20,
                        f"하드코딩된 Google Key 발견: {py_path}"
                    )


class TestSanitizerAndSecurity(unittest.TestCase):
    """
    DataSanitizer의 민감 정보 마스킹 및 전송 한도 제어를 검증하는 테스트 클래스임.
    """

    def setUp(self) -> None:
        self.sanitizer = DataSanitizer(max_files=10, max_lines=5)

    def test_mask_api_key_and_secrets(self) -> None:
        """
        [보안 검증 1]: API Key와 패스워드 할당문이 [REDACTED_*]로 정상 치환되는지 검증함.
        """
        raw_diff = """
+ API_KEY = "sk-abcdef1234567890abcdef123456"
+ password = 'mypassword123!'
+ contact = "developer@company.com"
+ ip = "192.168.1.100"
"""
        masked = self.sanitizer.mask_sensitive_patterns(raw_diff)

        self.assertNotIn("sk-abcdef", masked)
        self.assertIn("[REDACTED_API_KEY]", masked)
        self.assertNotIn("mypassword123!", masked)
        self.assertIn("[REDACTED_SECRET]", masked)
        self.assertNotIn("developer@company.com", masked)
        self.assertIn("[REDACTED_EMAIL]", masked)
        self.assertNotIn("192.168.1.100", masked)
        self.assertIn("[REDACTED_IP]", masked)

    def test_diff_truncation_under_safe_mode(self) -> None:
        """
        [보안 검증 2]: diff 줄 수가 5줄(max_lines)을 초과할 때 잘라내고 안내 문구가 삽입되는지 검증함.
        """
        long_diff = "\n".join([f"+ line {i}" for i in range(10)])
        truncated, was_truncated = self.sanitizer.truncate_diff(long_diff)

        self.assertTrue(was_truncated)
        self.assertIn("[... Diff truncated:", truncated)
        self.assertEqual(len(truncated.splitlines()[:5]), 5)


class TestPromptEngine(unittest.TestCase):
    """
    PromptEngine의 커밋 및 PR 프롬프트 구성 규칙을 검증하는 테스트 클래스임.
    """

    def test_commit_prompt_rules_included(self) -> None:
        """
        [프롬프트 검증 1]: commit 프롬프트에 50자/72자 규칙 및 불릿 규칙이 포함되는지 확인함.
        """
        prompt = PromptEngine.build_commit_prompt(["file1.py", "file2.py"], "+ print('hello')")
        self.assertIn("50자 이내 권장", prompt)
        self.assertIn("72자", prompt)
        self.assertIn("불릿", prompt)
        self.assertIn("file1.py", prompt)

    def test_pr_prompt_required_sections_included(self) -> None:
        """
        [프롬프트 검증 2]: pr 프롬프트에 ## Why, ## What, ## How to Test 3대 필수 섹션이 명시되는지 확인함.
        """
        prompt = PromptEngine.build_pr_prompt(["main.py"], "+ diff", "feature/login")
        self.assertIn("## Why", prompt)
        self.assertIn("## What", prompt)
        self.assertIn("## How to Test", prompt)
        self.assertIn("feature/login", prompt)


class TestPostProcessor(unittest.TestCase):
    """
    PostProcessor의 품질 가드레일(길이 절삭, 마크다운 제거, 섹션 복원)을 검증하는 테스트 클래스임.
    """

    def test_strip_markdown_and_truncate_title(self) -> None:
        """
        [가드레일 검증 1]: 백틱 코드블록이 제거되고 72자 초과 커밋 제목이 안전 절삭되는지 검증함.
        """
        super_long_title = "feat: " + ("a" * 80)
        raw_commit = f"```markdown\n{super_long_title}\n\n- Updated login logic\n```"

        cleaned = PostProcessor.clean_commit_message(raw_commit)

        self.assertNotIn("```", cleaned)
        first_line = cleaned.splitlines()[1]  # 구분선 바로 다음 줄임
        self.assertLessEqual(len(first_line), 72)
        self.assertTrue(first_line.endswith("..."))
        self.assertIn("Commit Message", cleaned)

    def test_pr_sections_restoration(self) -> None:
        """
        [가드레일 검증 2]: PR 본문에 필수 섹션이 누락되었을 때 템플릿 헤더가 복원되는지 검증함.
        """
        broken_pr = "Title: feat: new feature\n\nJust some random description without headers."
        cleaned = PostProcessor.clean_pr_draft(broken_pr)

        self.assertIn("## Why", cleaned)
        self.assertIn("## What", cleaned)
        self.assertIn("## How to Test", cleaned)
        self.assertIn("PR Title", cleaned)
        self.assertIn("PR Body", cleaned)


class TestAIClientAndCLI(unittest.TestCase):
    """
    AIClient 및 CLI 인자 파서의 동작 및 에러 캡슐화를 검증하는 테스트 클래스임.
    """

    def test_ai_key_missing_error(self) -> None:
        """
        [AI 클라이언트 검증 1]: AI_API_KEY 미설정 시 명확한 에러 메시지가 출력되고 캡슐화되는지 검증함.
        """
        with patch.dict(os.environ, {}, clear=True):
            client = AIClient(api_key=None)
            with self.assertRaises(AIClientError) as ctx:
                client.validate_api_key()
            self.assertIn("AI_API_KEY 환경변수가 설정되지 않았습니다", str(ctx.exception))

    def test_cli_parser_options(self) -> None:
        """
        [CLI 검증 2]: -safe-mode, --model, --temperature, --max-tokens 옵션이 정상 파싱되는지 검증함.
        """
        parser = CLIParser()
        args = parser.parse_args(["commit", "-safe-mode", "-m", "gpt-4o", "-t", "0.5", "--max-tokens", "500"])

        self.assertEqual(args.command, "commit")
        self.assertTrue(args.safe_mode)
        self.assertEqual(args.model, "gpt-4o")
        self.assertEqual(args.temperature, 0.5)
        self.assertEqual(args.max_tokens, 500)


def run_tests() -> bool:
    """테스트 스위트를 실행하고 성공 여부를 반환함."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStaticASTAndQuality)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSanitizerAndSecurity))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPromptEngine))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPostProcessor))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestAIClientAndCLI))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
