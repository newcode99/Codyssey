"""
B5-2 Mini Git - 커밋 노드 데이터 모델
설계 목적: Git 커밋 노드의 메타데이터 무결성을 보장하고 표현 계층을 분리함.
데이터 필드: hash, message, author, timestamp, parents를 보관함.
"""
from typing import List


class CommitNode:
    """
    Git 커밋 1개의 메타데이터를 저장하는 핵심 데이터 노드 클래스임.
    불변성을 지향하며 그래프 탐색 및 역색인 등록의 기본 단위가 됨.
    """

    def __init__(
        self,
        commit_hash: str,
        message: str,
        author: str,
        timestamp: str,
        parents: List[str]
    ):
        """
        커밋 노드를 초기화함.
        commit_hash: 세션 내 유일한 6자리 이상의 식별자임.
        message: 커밋 메시지 본문임.
        author: 커밋 작성자 이름임.
        timestamp: 커밋 생성 시각 문자열임 (YYYY-MM-DD HH:MM:SS 규격).
        parents: 직전 부모 커밋 해시 목록임 (루트 커밋의 경우 빈 리스트임).
        """
        self.hash: str = commit_hash
        self.message: str = message
        self.author: str = author
        self.timestamp: str = timestamp
        self.parents: List[str] = list(parents)

    def to_dict(self) -> dict:
        """커밋 메타데이터를 딕셔너리 형태로 직렬화하여 반환함."""
        return {
            "hash": self.hash,
            "message": self.message,
            "author": self.author,
            "timestamp": self.timestamp,
            "parents": list(self.parents)
        }

    def __repr__(self) -> str:
        """디버깅을 위한 문자열 표현을 반환함."""
        return f"CommitNode(hash={self.hash}, author={self.author}, parents={self.parents})"
