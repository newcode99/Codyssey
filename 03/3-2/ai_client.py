"""
B3-2 AI Git Generator - AI REST 통신 및 예외 캡슐화 클라이언트 모듈
설계 목적: 외부 의존성(SDK) 없이 Python 표준 urllib.request 기반으로 AI API를 호출함.
보안 및 비용 관리: AI_API_KEY 환경변수를 검증하고 하드코딩을 원천 배제하며, 1회 실행 1회 호출 로깅을 수행함.
예외 안전성: 401(인증 실패), 404, 429(속도 제한), 5xx, 네트워크 단절 등 모든 예외를 Traceback 0%로 캡슐화함.
주석 규격: 명사형 및 개조식(~함, ~임, ~를 위한) 준수함.
"""
import json
import os
import sys
import urllib.error
import urllib.request
from typing import Any, Dict, Optional, Tuple


class AIClientError(Exception):
    """AI 통신 도메인 전용 예외 클래스임."""
    pass


class AIClient:
    """
    AI REST API 엔드포인트와 통신하여 텍스트 생성을 수행하는 클라이언트 클래스임.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "gemini-1.5-flash",
        temperature: float = 0.2,
        max_tokens: int = 1000,
        endpoint_override: Optional[str] = None
    ) -> None:
        """
        API 키 및 통신 파라미터를 초기화함.
        api_key 인자가 전달되지 않으면 AI_API_KEY 환경변수에서 로드함.
        """
        self.api_key: Optional[str] = api_key or os.getenv("AI_API_KEY")
        self.model: str = model
        self.temperature: float = temperature
        self.max_tokens: int = max_tokens
        self.endpoint_override: Optional[str] = endpoint_override or os.getenv("AI_API_ENDPOINT")
        self.call_count: int = 0

    def validate_api_key(self) -> None:
        """
        API Key 존재 여부를 확인함.
        누락 시 사용자 친화적인 에러 메시지를 출력하고 예외를 발생시킴.
        """
        if not self.api_key or not self.api_key.strip():
            error_msg = (
                "[ERROR] AI_API_KEY 환경변수가 설정되지 않았습니다.\n"
                "## 예) export AI_API_KEY=\"YOUR_KEY\""
            )
            raise AIClientError(error_msg)

    def _build_request_payload(self, prompt: str) -> Tuple[str, Dict[str, str], Dict[str, Any]]:
        """
        Gemini REST 규격 또는 OpenAI 호환 REST 규격에 맞는 URL과 페이로드를 생성함.
        """
        # 엔드포인트 URL 결정임
        if self.endpoint_override:
            # 커스텀 OpenAI 호환 엔드포인트 규격임
            url = self.endpoint_override
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            body = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
        else:
            # 기본 Google Gemini API v1beta 엔드포인트 규격임
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            headers = {"Content-Type": "application/json"}
            body = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": self.temperature,
                    "maxOutputTokens": self.max_tokens
                }
            }

        return url, headers, body

    def generate_text(self, prompt: str) -> str:
        """
        AI API를 1회 호출하여 생성된 텍스트 응답을 반환함.
        네트워크, 인증, 속도 제한 등 모든 예외를 안전하게 캡슐화함.
        """
        self.validate_api_key()

        url, headers, body = self._build_request_payload(prompt)
        json_data = json.dumps(body).encode("utf-8")

        req = urllib.request.Request(url, data=json_data, headers=headers, method="POST")

        self.call_count += 1

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                status_code = response.getcode()
                response_body = response.read().decode("utf-8")
                response_json = json.loads(response_body)

                # 응답 파싱임 (Gemini 규격 vs OpenAI 규격)
                if "candidates" in response_json:
                    # Gemini 응답 형식임
                    candidate = response_json["candidates"][0]
                    content = candidate.get("content", {})
                    parts = content.get("parts", [])
                    if parts and "text" in parts[0]:
                        return parts[0]["text"].strip()
                    return ""
                elif "choices" in response_json:
                    # OpenAI 호환 응답 형식임
                    return response_json["choices"][0]["message"]["content"].strip()
                else:
                    return response_body.strip()

        except urllib.error.HTTPError as http_err:
            error_detail = ""
            try:
                error_detail = http_err.read().decode("utf-8")
            except Exception:
                pass

            if http_err.code == 400:
                raise AIClientError(f"API 요청 형식 오류 (400 Bad Request): {error_detail or http_err.reason}")
            elif http_err.code == 401 or http_err.code == 403:
                raise AIClientError(f"API Key 인증/권한 실패 ({http_err.code}): 유효한 API Key인지 확인 필요함.")
            elif http_err.code == 429:
                raise AIClientError("API 사용 한도 초과 (429 Too Many Requests): 잠시 후 다시 시도 필요함.")
            else:
                raise AIClientError(f"AI API 서버 오류 ({http_err.code}): {http_err.reason}")

        except urllib.error.URLError as url_err:
            raise AIClientError(f"네트워크 연결 실패: {url_err.reason}")

        except TimeoutError:
            raise AIClientError("AI API 요청 시간 초과 (Timeout 30s): 네트워크 상태를 확인 바람.")

        except Exception as general_err:
            raise AIClientError(f"AI 응답 처리 중 예상치 못한 오류 발생: {str(general_err)}")
