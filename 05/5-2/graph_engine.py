"""
B5-2 Mini Git - 커밋 그래프 및 탐색 알고리즘 엔진
설계 목적: 커밋 간의 DAG(방향성 비순환 그래프) 구조를 유지하고,
위상 정렬(Kahn), 무방향 BFS 최단 경로 탐색, 조상 역추적을 순수 자료형으로 구현함.
제약 준수: networkx 등 외부 라이브러리 일체 배제, Python 표준 정렬 API(sorted, sort) 일체 배제함.
"""
from collections import deque
from typing import Dict, List, Optional, Set, Tuple
from models import CommitNode
from sort_engine import merge_sort


class CommitGraph:
    """
    커밋 노드들의 관계를 관리하고 그래프 탐색 알고리즘을 수행하는 핵심 그래프 엔진 클래스임.
    """

    def __init__(self) -> None:
        """
        커밋 그래프 저장소를 초기화함.
        commits: 커밋 해시(hash)를 키로 하고 CommitNode를 값으로 하는 해시맵임.
        """
        self.commits: Dict[str, CommitNode] = {}

    def add_commit(self, commit: CommitNode) -> None:
        """신규 커밋 노드를 그래프 저장소에 등록함."""
        self.commits[commit.hash] = commit

    def get_commit(self, commit_hash: str) -> Optional[CommitNode]:
        """해시로 커밋 노드를 조회함. 존재하지 않으면 None을 반환함."""
        return self.commits.get(commit_hash)

    def contains(self, commit_hash: str) -> bool:
        """커밋 해시의 존재 여부를 O(1)로 확인하여 반환함."""
        return commit_hash in self.commits

    def topological_sort(self) -> List[CommitNode]:
        """
        진입차수(in-degree) 기반 Kahn 알고리즘을 사용하여 부모 커밋이 자식 커밋보다
        항상 먼저 출력되도록 위상 정렬을 수행함.
        시간 복잡도: O(V + E)
        결정론적 출력 보장: 큐에 존재하는 후보 노드들을 커스텀 병합 정렬(merge_sort)로
        timestamp 오름차순, 동일 시각일 경우 hash 사전순으로 정렬하여 인출함.
        """
        if not self.commits:
            return []

        # 1. 인접 리스트(부모 -> 자식) 및 진입차수(in_degree) 계산임
        # Git 관계에서 인과 흐름은 '부모 -> 자식'이므로 자식의 진입차수는 부모의 수임
        in_degree: Dict[str, int] = {h: 0 for h in self.commits}
        children: Dict[str, List[str]] = {h: [] for h in self.commits}

        for commit_hash, node in self.commits.items():
            for parent_hash in node.parents:
                if parent_hash in self.commits:
                    children[parent_hash].append(commit_hash)
                    in_degree[commit_hash] += 1

        # 2. 진입차수가 0인 노드(루트 커밋들)를 초기 대기열에 수집함
        zero_in_degree: List[str] = [
            h for h, degree in in_degree.items() if degree == 0
        ]

        result_nodes: List[CommitNode] = []

        # 3. Kahn 알고리즘 반복 루프 수행임
        while zero_in_degree:
            # 결정론적 출력을 위해 커스텀 정렬기로 대기열을 정렬함 (timestamp, hash 기준)
            def sort_key(h: str) -> Tuple[str, str]:
                node = self.commits[h]
                return (node.timestamp, node.hash)

            sorted_candidates = merge_sort(zero_in_degree, key=sort_key)
            current_hash = sorted_candidates[0]
            # 인출된 노드를 제외한 나머지로 zero_in_degree를 갱신함
            zero_in_degree = sorted_candidates[1:]

            result_nodes.append(self.commits[current_hash])

            # 자식 노드들의 진입차수를 감소시키고 0이 되면 대기열에 추가함
            for child_hash in children[current_hash]:
                in_degree[child_hash] -= 1
                if in_degree[child_hash] == 0:
                    zero_in_degree.append(child_hash)

        # 사이클이 발생하지 않았다면 모든 노드가 포함됨
        return result_nodes

    def find_shortest_path(self, start_hash: str, end_hash: str) -> Optional[List[str]]:
        """
        커밋과 부모 사이의 관계를 무방향 간선(Undirected Edge)으로 간주하여
        너비 우선 탐색(BFS) 기반으로 최단 경로(간선 수 최소)를 탐색함.
        경로가 없을 경우 None을 반환함.
        최단 경로가 다수 존재할 경우:
        'hash1->hash2->...' 문자열 기준 사전순(Lexicographical)으로 가장 작은 경로를 선택함.
        시간 복잡도: O(V + E)
        """
        if start_hash not in self.commits or end_hash not in self.commits:
            return None

        # 시작점과 도착점이 같은 경우임
        if start_hash == end_hash:
            return [start_hash]

        # 1. 무방향 인접 리스트(Undirected Adjacency List) 구축임
        undirected_adj: Dict[str, List[str]] = {h: [] for h in self.commits}
        for commit_hash, node in self.commits.items():
            for parent_hash in node.parents:
                if parent_hash in self.commits:
                    undirected_adj[commit_hash].append(parent_hash)
                    undirected_adj[parent_hash].append(commit_hash)

        # 2. 최단 경로 탐색을 위한 BFS 큐 및 방문/거리 추적임
        queue: deque[Tuple[str, List[str]]] = deque([(start_hash, [start_hash])])
        shortest_distance: Optional[int] = None
        candidate_paths: List[List[str]] = []
        min_distance_to_node: Dict[str, int] = {start_hash: 0}

        while queue:
            current_node, current_path = queue.popleft()
            current_dist = len(current_path) - 1

            # 이미 발견된 최단 거리보다 긴 탐색은 즉시 중단함
            if shortest_distance is not None and current_dist > shortest_distance:
                break

            # 목적지 도달 검사임
            if current_node == end_hash:
                if shortest_distance is None:
                    shortest_distance = current_dist
                if current_dist == shortest_distance:
                    candidate_paths.append(current_path)
                continue

            # 인접 노드 탐색임
            for neighbor in undirected_adj[current_node]:
                new_dist = current_dist + 1
                # 인접 노드 방문 조건: 최초 방문이거나 동일 최단 거리로 도달한 경우임
                if neighbor not in min_distance_to_node or new_dist <= min_distance_to_node[neighbor]:
                    min_distance_to_node[neighbor] = new_dist
                    queue.append((neighbor, current_path + [neighbor]))

        if not candidate_paths:
            return None

        # 3. 최단 경로 중 문자열 표현 기준 사전순 최소 경로 선택임
        def path_key(path: List[str]) -> str:
            return "->".join(path)

        sorted_paths = merge_sort(candidate_paths, key=path_key)
        return sorted_paths[0]

    def get_ancestors(self, commit_hash: str) -> List[str]:
        """
        해당 커밋에서 부모 링크(parents)를 타고 도달 가능한 모든 상위 조상 커밋 목록을 중복 없이 추출함.
        BFS 순회 및 방문 집합(visited)을 사용하여 브랜치 병합 시의 중복 탐색을 방지함.
        반환값은 일관된 순서를 위해 커스텀 정렬기(merge_sort)로 정렬하여 반환함.
        """
        if commit_hash not in self.commits:
            return []

        visited_ancestors: Set[str] = set()
        queue: deque[str] = deque()

        # 직계 부모들부터 탐색 큐에 삽입함 (자기 자신은 조상에 포함되지 않음)
        start_node = self.commits[commit_hash]
        for parent in start_node.parents:
            if parent in self.commits and parent not in visited_ancestors:
                visited_ancestors.add(parent)
                queue.append(parent)

        while queue:
            curr_hash = queue.popleft()
            curr_node = self.commits.get(curr_hash)
            if not curr_node:
                continue

            for parent in curr_node.parents:
                if parent in self.commits and parent not in visited_ancestors:
                    visited_ancestors.add(parent)
                    queue.append(parent)

        # 결정론적 결과 반환을 위해 커스텀 병합 정렬로 정렬함
        return merge_sort(list(visited_ancestors))
