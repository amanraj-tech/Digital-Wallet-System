"""
Sorting Algorithms
------------------
Real, from-scratch implementations used to sort transaction records.
Each function takes a list and a `key` function (like Python's sorted())
so they can be reused for any field (amount, date, name, ...), plus a
`reverse` flag.

- insertion_sort : O(n^2) worst case, good for small / nearly-sorted lists.
- merge_sort     : O(n log n), stable, used as the default for larger lists.
- quick_sort     : O(n log n) average, used to demonstrate partitioning.
"""


def insertion_sort(items, key=lambda x: x, reverse=False):
    arr = list(items)
    for i in range(1, len(arr)):
        current = arr[i]
        current_key = key(current)
        j = i - 1
        while j >= 0 and _should_move(key(arr[j]), current_key, reverse):
            arr[j + 1] = arr[j]
            j -= 1
        arr[j + 1] = current
    return arr


def _should_move(a_key, b_key, reverse):
    return (a_key > b_key) if not reverse else (a_key < b_key)


def merge_sort(items, key=lambda x: x, reverse=False):
    arr = list(items)
    if len(arr) <= 1:
        return arr
    mid = len(arr) // 2
    left = merge_sort(arr[:mid], key, reverse)
    right = merge_sort(arr[mid:], key, reverse)
    return _merge(left, right, key, reverse)


def _merge(left, right, key, reverse):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        take_left = (key(left[i]) <= key(right[j])) if not reverse else (key(left[i]) >= key(right[j]))
        if take_left:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result


def quick_sort(items, key=lambda x: x, reverse=False):
    arr = list(items)
    _quick_sort(arr, 0, len(arr) - 1, key, reverse)
    return arr


def _quick_sort(arr, low, high, key, reverse):
    if low < high:
        pivot_index = _partition(arr, low, high, key, reverse)
        _quick_sort(arr, low, pivot_index - 1, key, reverse)
        _quick_sort(arr, pivot_index + 1, high, key, reverse)


def _partition(arr, low, high, key, reverse):
    pivot = key(arr[high])
    i = low - 1
    for j in range(low, high):
        condition = (key(arr[j]) <= pivot) if not reverse else (key(arr[j]) >= pivot)
        if condition:
            i += 1
            arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1], arr[high] = arr[high], arr[i + 1]
    return i + 1


# Map of sort option -> (algorithm, key function) used by the API layer.
SORT_ALGORITHMS = {
    "insertion": insertion_sort,
    "merge": merge_sort,
    "quick": quick_sort,
}
