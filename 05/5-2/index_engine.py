"""
B5-2 Mini Git - 역색인(Inverted Index) 검색 엔진
설계 목적: 전체 커밋 순회(O(N))를 배제하고 O(1) 시간 복잡도로 키워드 및 작성자별 커밋 후보군을 색인함.
자료구조: 해시 테이블 기반 매핑 dict[str, set[str]]을 사용함.
"""
from typing import Dict, List, Set
from models import CommitNode
from sort_engine import merge_sort


class InvertedIndex:
    """
    커밋 메시지 토큰 및 작성자명을 인덱싱하여 빠른 조회를 제공하는 역색인 클래스임.
    """

    def __init__(self) -> None:
        """
        역색인 저장소 맵을 초기화함.
        keyword_map: 소문자 정규화된 단어 토큰 -> 커밋 해시 집합 매핑임.
        author_map: 소문자 정규화된 작성자 이름 -> 커밋 해시 집합 매핑임.
        """
        self.keyword_map: Dict[str, Set[str]] = {}
        self.author_map: Dict[str, Set[str]] = {}

    def add_commit(self, commit: CommitNode) -> None:
        """
        신규 커밋 노드를 역색인 테이블에 등록함.
        메시지는 공백(split) 기준으로 분리하고 소문자(lower) 정규화를 적용함.
        작성자명 역시 소문자로 정규화하여 등록함.
        """
        # 1. 메시지 키워드 역색인 등록
        words = commit.message.split()
        for word in words:
            normalized_keyword = word.lower()
            if normalized_keyword not in self.keyword_map:
                self.keyword_map[normalized_keyword] = set()
            self.keyword_map[normalized_keyword].add(commit.hash)

        # 2. 작성자명 역색인 등록
        normalized_author = commit.author.lower()
        if normalized_author not in self.author_map:
            self.author_map[normalized_author] = set()
        self.author_map[normalized_author].add(commit.hash)

    def search_keyword(self, keyword: str) -> List[str]:
        """
        주어진 키워드로 등록된 커밋 해시 목록을 O(1)로 조회함.
        일관된 결과 조회를 위해 커스텀 병합 정렬(merge_sort)로 정렬하여 반환함.
        """
        normalized_keyword = keyword.lower()
        hash_set = self.keyword_map.get(normalized_keyword, set())
        # 커스텀 정렬기로 해시 사전순 정렬을 수행함 (표준 sorted 사용 금지 규격 준수)
        return merge_sort(list(hash_set))

    def search_author(self, author: str) -> List[str]:
        """
        주어진 작성자명으로 등록된 커밋 해시 목록을 O(1)로 조회함.
        일관된 결과 조회를 위해 커스텀 병합 정렬(merge_sort)로 정렬하여 반환함.
        """
        normalized_author = author.lower()
        hash_set = self.author_map.get(normalized_author, set())
        # 커스텀 정렬기로 해시 사전순 정렬을 수행함
        return merge_sort(list(hash_set))
