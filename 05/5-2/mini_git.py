"""
B5-2 Mini Git - 코어 비즈니스 파사드 엔진
설계 목적: Git 저장소의 상태 머신(초기화, 브랜치, HEAD, 커밋)을 총괄하고,
그래프 엔진, 역색인 엔진, 정렬 엔진을 유기적으로 조율하여 비즈니스 로직을 수행함.
제약 준수: 파이썬 표준 정렬 API 및 외부 라이브러리 일체 배제, 주석 개조식 규격 준수함.
"""
from datetime import datetime
import hashlib
from typing import Dict, List, Optional
from graph_engine import CommitGraph
from index_engine import InvertedIndex
from models import CommitNode
from sort_engine import merge_sort


class MiniGit:
    """
    Mini Git CLI의 모든 핵심 명령어 로직과 저장소 상태를 관리하는 파사드 클래스임.
    """

    def __init__(self) -> None:
        """
        저장소 상태 변수를 초기화함.
        초기 상태는 미초기화(is_initialized=False) 상태임.
        """
        self.is_initialized: bool = False
        self.current_user: Optional[str] = None
        # 브랜치명 -> 최신 커밋 해시 매핑임 (커밋이 없으면 None임)
        self.branches: Dict[str, Optional[str]] = {}
        self.head_branch: Optional[str] = None
        self.graph: CommitGraph = CommitGraph()
        self.index: InvertedIndex = InvertedIndex()
        self._hash_counter: int = 1

    def init(self, user_name: str) -> str:
        """
        저장소를 초기화함.
        기본 브랜치 'main'을 생성하고 HEAD를 'main'으로 설정함.
        현재 사용자를 등록하고 초기화 완료 메시지를 반환함.
        """
        self.is_initialized = True
        self.current_user = user_name
        self.branches = {"main": None}
        self.head_branch = "main"
        self.graph = CommitGraph()
        self.index = InvertedIndex()
        self._hash_counter = 1

        return (
            f"Initialized repository.\n"
            f"Current branch: {self.head_branch}\n"
            f"Current user: {self.current_user}"
        )

    def branch(self, branch_name: str) -> str:
        """
        신규 브랜치 포인터를 생성함.
        현재 활성 브랜치가 가리키는 커밋을 동일하게 가리키도록 설정함.
        """
        if not self.is_initialized:
            return "(error) Repository not initialized"

        if not branch_name:
            return "(error) Invalid args"

        if branch_name in self.branches:
            return f"(error) Branch already exists: {branch_name}"

        # 현재 HEAD가 가리키는 브랜치의 최신 커밋을 참조함
        current_commit_hash = self.branches.get(self.head_branch, None)
        self.branches[branch_name] = current_commit_hash

        return f"Created branch: {branch_name}"

    def switch(self, branch_name: str) -> str:
        """
        HEAD 포인터를 대상 브랜치로 전환함.
        미등록 브랜치일 경우 Unknown branch 표준 에러를 반환함.
        """
        if not self.is_initialized:
            return "(error) Repository not initialized"

        if not branch_name:
            return "(error) Invalid args"

        if branch_name not in self.branches:
            return f"(error) Unknown branch: {branch_name}"

        self.head_branch = branch_name
        return f"Switched to branch: {branch_name}"

    def _generate_unique_hash(self, message: str) -> str:
        """
        세션 내 중복되지 않는 6자리 고유 해시 문자열을 생성하는 내부 헬퍼 함수임.
        시간, 메시지, 유저, 내부 카운터를 혼합하여 sha1 6자리를 도출함.
        """
        while True:
            raw_data = f"{self._hash_counter}:{self.current_user}:{message}:{datetime.now().isoformat()}"
            digest = hashlib.sha1(raw_data.encode("utf-8")).hexdigest()[:6]
            self._hash_counter += 1
            if not self.graph.contains(digest):
                return digest

    def commit(self, message: str, custom_timestamp: Optional[str] = None) -> str:
        """
        신규 커밋을 생성함.
        현재 활성 브랜치의 최신 커밋을 부모(parents)로 설정함.
        새 커밋 해시를 발급하고 그래프 및 역색인에 등록 후 브랜치 포인터를 갱신함.
        """
        if not self.is_initialized:
            return "(error) Repository not initialized"

        if not message:
            return "(error) Invalid args"

        parent_hash = self.branches.get(self.head_branch)
        parents = [parent_hash] if parent_hash else []

        commit_hash = self._generate_unique_hash(message)
        timestamp = custom_timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        node = CommitNode(
            commit_hash=commit_hash,
            message=message,
            author=self.current_user or "Unknown",
            timestamp=timestamp,
            parents=parents
        )

        # 그래프 및 역색인 등록임
        self.graph.add_commit(node)
        self.index.add_commit(node)

        # 현재 활성 브랜치의 최신 커밋 갱신임
        self.branches[self.head_branch] = commit_hash

        return f"[{self.head_branch} {commit_hash}] {message}"

    def log(self, sort_by: Optional[str] = None) -> str:
        """
        커밋 히스토리 로그를 출력함.
        기본 옵션: 부모 커밋이 자식 커밋보다 먼저 출력되는 위상 정렬 순서임.
        --sort-by=date: 생성 시각 기준 오름차순 정렬 (커스텀 병합 정렬 사용함).
        --sort-by=author: 작성자 이름 기준 사전순 정렬 (커스텀 병합 정렬 사용함).
        """
        if not self.is_initialized:
            return "(error) Repository not initialized"

        if not self.graph.commits:
            return "No commits yet."

        nodes: List[CommitNode]

        if sort_by == "date":
            # 날짜(timestamp) 기준 정렬임 (동률 시 hash 사전순)
            def date_key(node: CommitNode):
                return (node.timestamp, node.hash)
            nodes = merge_sort(list(self.graph.commits.values()), key=date_key)
        elif sort_by == "author":
            # 작성자(author) 기준 정렬임 (동률 시 timestamp, hash 순)
            def author_key(node: CommitNode):
                return (node.author, node.timestamp, node.hash)
            nodes = merge_sort(list(self.graph.commits.values()), key=author_key)
        elif sort_by is None:
            # 위상 정렬(Topological Sort) 순서임
            nodes = self.graph.topological_sort()
        else:
            return f"(error) Invalid sort-by option: {sort_by}"

        output_lines: List[str] = []
        for node in nodes:
            # 해당 커밋을 가리키고 있는 브랜치 목록을 수집함
            pointing_branches = [
                b_name for b_name, b_hash in self.branches.items() if b_hash == node.hash
            ]
            pointing_branches = merge_sort(pointing_branches)

            if pointing_branches:
                branch_tag = f" [{', '.join(pointing_branches)}]"
            else:
                branch_tag = ""

            header = f"commit {node.hash} ({node.author}, {node.timestamp}){branch_tag}"
            output_lines.append(f"{header}\n{node.message}")

        return "\n\n".join(output_lines)

    def path(self, commit1: str, commit2: str) -> str:
        """
        두 커밋 사이의 무방향 간선 기반 최단 경로를 탐색하여 출력함.
        다중 경로 발생 시 사전순 최소 경로를 채택함.
        도달 불가 시 No path를 출력함.
        """
        if not self.is_initialized:
            return "(error) Repository not initialized"

        if not commit1 or not commit2:
            return "(error) Invalid args"

        if not self.graph.contains(commit1):
            return f"(error) Unknown commit: {commit1}"
        if not self.graph.contains(commit2):
            return f"(error) Unknown commit: {commit2}"

        shortest_path = self.graph.find_shortest_path(commit1, commit2)
        if not shortest_path:
            return "No path"

        return f"Path: {' -> '.join(shortest_path)}"

    def ancestors(self, commit_hash: str) -> str:
        """
        지정된 커밋의 모든 상위 조상 커밋 목록을 추출하여 출력함.
        """
        if not self.is_initialized:
            return "(error) Repository not initialized"

        if not commit_hash:
            return "(error) Invalid args"

        if not self.graph.contains(commit_hash):
            return f"(error) Unknown commit: {commit_hash}"

        ancestor_hashes = self.graph.get_ancestors(commit_hash)
        if not ancestor_hashes:
            return f"Ancestors of {commit_hash}: None"

        lines = [f"Ancestors of {commit_hash}:"]
        for anc_hash in ancestor_hashes:
            anc_node = self.graph.get_commit(anc_hash)
            if anc_node:
                lines.append(f"- {anc_hash}: {anc_node.message}")

        return "\n".join(lines)

    def search(self, query: str, is_author: bool = False) -> str:
        """
        역색인 엔진을 활용하여 키워드 또는 작성자 기준 커밋 검색을 수행함.
        시간 복잡도 O(1)로 후보군 해시 목록을 추출한 뒤 결과를 렌더링함.
        """
        if not self.is_initialized:
            return "(error) Repository not initialized"

        if not query:
            return "(error) Invalid args"

        if is_author:
            matched_hashes = self.index.search_author(query)
        else:
            matched_hashes = self.index.search_keyword(query)

        count = len(matched_hashes)
        unit = "commit" if count == 1 else "commits"

        if count == 0:
            return f"Found 0 {unit}:"

        lines = [f"Found {count} {unit}:\n"]
        for c_hash in matched_hashes:
            node = self.graph.get_commit(c_hash)
            if node:
                lines.append(f"- {node.hash}: {node.message}")

        return "\n".join(lines)
