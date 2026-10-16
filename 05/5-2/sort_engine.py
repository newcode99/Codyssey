"""
B5-2 Mini Git - 커스텀 정렬 엔진 모듈
설계 목적: Python 표준 정렬 API(sorted, list.sort)를 일체 사용하지 않고 O(N log N) 안정 정렬을 제공함.
주요 알고리즘: 분할 정복(Divide & Conquer) 기반 병합 정렬(Merge Sort)임.
"""
from typing import Any, Callable, List, Optional


def merge_sort(
    items: List[Any],
    key: Optional[Callable[[Any], Any]] = None,
    reverse: bool = False
) -> List[Any]:
    """
    분할 정복 기반으로 안정 정렬(Stable Sort)을 수행하는 병합 정렬 함수임.
    key 함수가 제공되면 해당 키 값을 기준으로 원소를 비교함.
    reverse가 True이면 내림차순으로 정렬함.
    시간 복잡도: O(N log N) (최선, 평균, 최악 동일함)
    공간 복잡도: O(N) (부분 리스트 병합을 위한 임시 공간임)
    """
    # 원소가 0개 또는 1개이면 이미 정렬된 상태임
    if len(items) <= 1:
        return list(items)

    mid = len(items) // 2
    left_sorted = merge_sort(items[:mid], key=key, reverse=reverse)
    right_sorted = merge_sort(items[mid:], key=key, reverse=reverse)

    return _merge(left_sorted, right_sorted, key=key, reverse=reverse)


def _merge(
    left: List[Any],
    right: List[Any],
    key: Optional[Callable[[Any], Any]],
    reverse: bool
) -> List[Any]:
    """
    정렬된 두 부분 리스트(left, right)를 순서에 맞춰 결합하는 내부 헬퍼 함수임.
    안정 정렬을 보장하기 위해 비교값이 동일할 때 left 원소를 우선 취함.
    """
    merged: List[Any] = []
    i = 0
    j = 0
    len_left = len(left)
    len_right = len(right)

    while i < len_left and j < len_right:
        left_val = key(left[i]) if key else left[i]
        right_val = key(right[j]) if key else right[j]

        # reverse 여부에 따른 비교 로직임
        if not reverse:
            # 오름차순: left_val <= right_val일 때 left를 먼저 넣어 안정 정렬을 보장함
            if left_val <= right_val:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        else:
            # 내림차순: left_val >= right_val일 때 left를 먼저 넣어 안정 정렬을 보장함
            if left_val >= right_val:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1

    # 남아있는 잔여 원소들을 순서대로 덧붙임
    while i < len_left:
        merged.append(left[i])
        i += 1
    while j < len_right:
        merged.append(right[j])
        j += 1

    return merged
