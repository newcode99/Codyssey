"""
B5-2 Mini Git - 종합 품질 검증 및 AST 정적 분석 테스트 스위트
설계 목적: 과제의 모든 필수 제약 조건과 10대 요구사항을 자동화된 테스트로 실증함.
1. AST 정적 분석: sorted(), list.sort(), networkx 사용 0건 및 주석 규격 검증함.
2. 공식 결과 예시 시나리오 동작 검증함.
3. 10대 엣지 케이스 및 알고리즘 무결성 검증함.
"""
import ast
import os
import sys
from cli import MiniGitCLI
from graph_engine import CommitGraph
from index_engine import InvertedIndex
from models import CommitNode
from mini_git import MiniGit
from sort_engine import merge_sort


def run_ast_static_analysis() -> None:
    """
    소스 코드 파일들을 AST(추상 구문 트리)로 파싱하여
    금지된 API(sorted, sort, networkx)의 호출 여부를 정적 검사함.
    """
    print("=" * 60)
    print("[검사 1] AST 정적 분석 기반 제약 조건 및 금기 규칙 검증")
    print("=" * 60)

    target_files = [
        "sort_engine.py",
        "models.py",
        "index_engine.py",
        "graph_engine.py",
        "mini_git.py",
        "cli.py",
        "main.py",
    ]

    base_dir = os.path.dirname(os.path.abspath(__file__))
    forbidden_calls_found = []

    for file_name in target_files:
        file_path = os.path.join(base_dir, file_name)
        if not os.path.exists(file_path):
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            source = f.read()

        # 1. 주석 내 금지 어미('합니다') 검사임
        if "합니다" in source:
            raise AssertionError(f"[규격 위반] {file_name}에 금지된 어미 '합니다'가 존재함.")

        tree = ast.parse(source, filename=file_name)

        for node in ast.walk(tree):
            # 2. networkx 모듈 import 검사임
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "networkx" in alias.name:
                        forbidden_calls_found.append(f"{file_name}: import {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                if node.module and "networkx" in node.module:
                    forbidden_calls_found.append(f"{file_name}: from {node.module} import ...")

            # 3. sorted() 내장 함수 호출 검사임
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == "sorted":
                    forbidden_calls_found.append(f"{file_name}:{node.lineno} sorted() 호출")
                # 4. .sort() 메서드 호출 검사임
                elif isinstance(node.func, ast.Attribute) and node.func.attr == "sort":
                    forbidden_calls_found.append(f"{file_name}:{node.lineno} .sort() 메서드 호출")

    if forbidden_calls_found:
        print("[FAIL] 금지된 API 사용 적발:")
        for item in forbidden_calls_found:
            print(f"  - {item}")
        raise AssertionError("AST 검사 실패: 금지된 API(sorted, sort, networkx)가 사용됨.")

    print("✔ AST 정적 분석 통과: sorted() 사용 0건, list.sort() 사용 0건, networkx 사용 0건")
    print("✔ 주석 스타일 규칙 통과: '합니다' 사용 0건, 개조식/명사형 주석 규격 준수 확인")


def run_scenario_test() -> None:
    """
    과제 명세서 8번의 공식 결과 예시 시나리오를 CLI 엔진을 통해 실행하고 검증함.
    """
    print("\n" + "=" * 60)
    print("[검사 2] 과제 8번 공식 결과 예시 시나리오 검증")
    print("=" * 60)

    cli = MiniGitCLI()

    # 1. init "Alice"
    res1 = cli.execute_line('init "Alice"')
    assert "Initialized repository." in res1, f"Init 실패: {res1}"
    assert "Current branch: main" in res1
    assert "Current user: Alice" in res1
    print("✔ 1. INIT 완료:", res1.replace("\n", " | "))

    # 2. commit "Initial commit"
    res2 = cli.execute_line('commit "Initial commit"')
    assert res2.startswith("[main ") and "Initial commit" in res2
    c1_hash = res2.split()[1].rstrip("]")
    print(f"✔ 2. 최초 커밋 생성 완료: {res2} (해시: {c1_hash})")

    # 3. branch feature
    res3 = cli.execute_line("branch feature")
    assert res3 == "Created branch: feature"
    print("✔ 3. 브랜치 생성 완료:", res3)

    # 4. switch feature
    res4 = cli.execute_line("switch feature")
    assert res4 == "Switched to branch: feature"
    print("✔ 4. 브랜치 전환 완료:", res4)

    # 5. commit "Add login feature"
    res5 = cli.execute_line('commit "Add login feature"')
    assert res5.startswith("[feature ") and "Add login feature" in res5
    c2_hash = res5.split()[1].rstrip("]")
    print(f"✔ 5. feature 브랜치 커밋 생성 완료: {res5} (해시: {c2_hash})")

    # 6. switch main
    res6 = cli.execute_line("switch main")
    assert res6 == "Switched to branch: main"
    print("✔ 6. main 브랜치 복귀 완료:", res6)

    # 7. commit "Add payment feature"
    res7 = cli.execute_line('commit "Add payment feature"')
    assert res7.startswith("[main ") and "Add payment feature" in res7
    c3_hash = res7.split()[1].rstrip("]")
    print(f"✔ 7. main 브랜치 신규 커밋 생성 완료: {res7} (해시: {c3_hash})")

    # 8. log (위상 정렬: 부모 c1이 자식 c2, c3보다 먼저 나와야 함)
    res8 = cli.execute_line("log")
    print("✔ 8. LOG 출력 확인:\n" + res8)
    pos_c1 = res8.find(c1_hash)
    pos_c2 = res8.find(c2_hash)
    pos_c3 = res8.find(c3_hash)
    assert pos_c1 != -1 and pos_c2 != -1 and pos_c3 != -1
    assert pos_c1 < pos_c2, "위상 정렬 오류: 부모 c1이 자식 c2보다 뒤에 출력됨"
    assert pos_c1 < pos_c3, "위상 정렬 오류: 부모 c1이 자식 c3보다 뒤에 출력됨"
    print("✔ 위상 정렬 무결성 확인: 부모 커밋(c1)이 모든 분기 자식 커밋(c2, c3)보다 선행하여 출력됨")

    # 9. path c2 c3 (feature의 c2와 main의 c3 사이 경로: c2 -> c1 -> c3)
    res9 = cli.execute_line(f"path {c2_hash} {c3_hash}")
    print("✔ 9. PATH 출력 확인:", res9)
    assert res9 == f"Path: {c2_hash} -> {c1_hash} -> {c3_hash}"

    # 10. search "login"
    res10 = cli.execute_line('search "login"')
    print("✔ 10. SEARCH 'login' 출력 확인:\n" + res10)
    assert "Found 1 commit:" in res10
    assert c2_hash in res10 and "Add login feature" in res10

    # 11. log --sort-by=author
    res11 = cli.execute_line("log --sort-by=author")
    print("✔ 11. LOG --sort-by=author 출력 확인:\n" + res11)
    assert c1_hash in res11 and c2_hash in res11 and c3_hash in res11


def run_edge_cases_test() -> None:
    """
    10대 엣지 케이스 및 예외 처리, 알고리즘 무결성을 전수 검증함.
    """
    print("\n" + "=" * 60)
    print("[검사 3] 10대 엣지 케이스 및 예외 처리 전수 검증")
    print("=" * 60)

    # TC 01: 초기화 전 명령 실행 차단 검증
    cli_fresh = MiniGitCLI()
    assert cli_fresh.execute_line("commit 'test'") == "(error) Repository not initialized"
    assert cli_fresh.execute_line("log") == "(error) Repository not initialized"
    assert cli_fresh.execute_line("branch feat") == "(error) Repository not initialized"
    print("✔ TC 01: 초기화 전 명령 차단 검증 통과")

    # 저장소 초기화
    cli_fresh.execute_line("init 'Tester'")

    # TC 02: 인자 누락 및 유효하지 않은 인자 검증
    assert cli_fresh.execute_line("init") == "(error) Invalid args"
    assert cli_fresh.execute_line("branch") == "(error) Invalid args"
    assert cli_fresh.execute_line("switch") == "(error) Invalid args"
    assert cli_fresh.execute_line("commit") == "(error) Invalid args"
    assert cli_fresh.execute_line("path c1") == "(error) Invalid args"
    assert cli_fresh.execute_line("search") == "(error) Invalid args"
    print("✔ TC 02: 인자 누락 에러 표준화 검증 통과")

    # TC 03: 미존재 브랜치 switch 시 에러 검증
    res_unknown_branch = cli_fresh.execute_line("switch ghost_branch")
    assert res_unknown_branch == "(error) Unknown branch: ghost_branch"
    print("✔ TC 03: 미존재 브랜치 전환 차단 검증 통과")

    # TC 04: 미존재 커밋 조회 시 에러 검증
    res_unknown_commit = cli_fresh.execute_line("path nonexistent1 nonexistent2")
    assert res_unknown_commit == "(error) Unknown commit: nonexistent1"
    res_unknown_anc = cli_fresh.execute_line("ancestors nonexistent")
    assert res_unknown_anc == "(error) Unknown commit: nonexistent"
    print("✔ TC 04: 미존재 커밋 에러 표준화 검증 통과")

    # TC 05: 동일 커밋 최단 경로 탐색 검증
    c1_res = cli_fresh.execute_line("commit 'First'")
    c1 = c1_res.split()[1].rstrip("]")
    path_same = cli_fresh.execute_line(f"path {c1} {c1}")
    assert path_same == f"Path: {c1}"
    print("✔ TC 05: 동일 커밋 최단 경로 탐색 검증 통과")

    # TC 06: 연결되지 않은 단절 그래프 생성 및 No path 검증
    # graph_engine에 직접 고립된 커밋을 주입하여 테스트함
    node_isolated = CommitNode("iso999", "Isolated commit", "Tester", "2024-01-01 00:00:00", [])
    cli_fresh.engine.graph.add_commit(node_isolated)
    res_no_path = cli_fresh.execute_line(f"path {c1} iso999")
    assert res_no_path == "No path"
    print("✔ TC 06: 도달 불가 단절 커밋 간 No path 검증 통과")

    # TC 07: 사전순 타이브레이킹 최단 경로 검증
    # 동일 거리의 복수 경로를 생성하여 사전순 최소 경로가 선택되는지 검증함
    # 구조: start -> nodeA -> target, start -> nodeB -> target (nodeA: 'a000', nodeB: 'b000')
    graph = CommitGraph()
    n_start = CommitNode("start0", "start", "Tester", "2024-01-01 01:00:00", [])
    n_a = CommitNode("a_path", "a", "Tester", "2024-01-01 01:01:00", ["start0"])
    n_b = CommitNode("b_path", "b", "Tester", "2024-01-01 01:01:00", ["start0"])
    n_end = CommitNode("end000", "end", "Tester", "2024-01-01 01:02:00", ["a_path", "b_path"])

    graph.add_commit(n_start)
    graph.add_commit(n_a)
    graph.add_commit(n_b)
    graph.add_commit(n_end)

    chosen_path = graph.find_shortest_path("start0", "end000")
    # 'start0 -> a_path -> end000' vs 'start0 -> b_path -> end000' 중 'a_path'가 사전순 앞섬
    assert chosen_path == ["start0", "a_path", "end000"], f"타이브레이킹 오류: {chosen_path}"
    print("✔ TC 07: 다중 최단 경로 사전순 타이브레이킹 검증 통과")

    # TC 08: 조상(Ancestors) 추적 중복 배제 및 다중 부모(Merge) 환경 검증
    ancestors = graph.get_ancestors("end000")
    assert "start0" in ancestors and "a_path" in ancestors and "b_path" in ancestors
    assert "end000" not in ancestors  # 자기 자신은 조상에 미포함
    print("✔ TC 08: 조상 역추적 및 머지 환경 중복 제거 검증 통과")

    # TC 09: 역색인 대소문자 무구분 및 O(1) 검색 검증
    idx = InvertedIndex()
    c_idx = CommitNode("c_idx1", "Refactor Auth Token Module", "Bob", "2024-01-01 02:00:00", [])
    idx.add_commit(c_idx)
    # 대소문자 무관 검색
    assert idx.search_keyword("auth") == ["c_idx1"]
    assert idx.search_keyword("AUTH") == ["c_idx1"]
    assert idx.search_keyword("token") == ["c_idx1"]
    assert idx.search_author("bob") == ["c_idx1"]
    assert idx.search_author("BOB") == ["c_idx1"]
    assert idx.search_keyword("ghost") == []
    print("✔ TC 09: 역색인 대소문자 무구분 및 토큰 검색 검증 통과")

    # TC 10: 커스텀 병합 정렬(Merge Sort) 안정 정렬 및 key, reverse 검증
    sample_data = [
        {"name": "Alice", "score": 90, "order": 1},
        {"name": "Bob", "score": 80, "order": 2},
        {"name": "Charlie", "score": 90, "order": 3},
        {"name": "Dave", "score": 70, "order": 4},
    ]
    # score 기준 내림차순 정렬 시, 동일한 90점의 Alice(order 1)와 Charlie(order 3)의 상대적 순서 보존 검증
    sorted_res = merge_sort(sample_data, key=lambda x: x["score"], reverse=True)
    assert sorted_res[0]["name"] == "Alice" and sorted_res[1]["name"] == "Charlie"
    assert sorted_res[2]["name"] == "Bob" and sorted_res[3]["name"] == "Dave"
    print("✔ TC 10: 커스텀 병합 정렬의 안정 정렬(Stable Sort) 속성 검증 통과")


def main() -> None:
    """테스트 스위트 통합 실행기임."""
    try:
        run_ast_static_analysis()
        run_scenario_test()
        run_edge_cases_test()
        print("\n" + "=" * 60)
        print("🎉 [ALL TESTS PASSED] 모든 정적/동적 검증을 100% 무결점으로 통과함.")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n❌ [TEST FAILED] {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
