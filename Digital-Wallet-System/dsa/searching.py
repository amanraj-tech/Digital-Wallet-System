"""
Searching Algorithms
--------------------
- linear_search : O(n), works on any unordered collection and any predicate.
  Used for multi-field / partial-match transaction search.
- binary_search : O(log n), requires the collection to be sorted on the
  comparison key first. Used for exact-match lookups (e.g. exact amount,
  exact transaction id) on data we already have sorted.
"""


def linear_search(items, predicate):
    """Return every item for which predicate(item) is True. O(n)."""
    return [item for item in items if predicate(item)]


def binary_search(sorted_items, target, key=lambda x: x):
    """Classic binary search for an exact match on `key`.
    `sorted_items` MUST already be sorted ascending by `key`.
    Returns the matching item or None. O(log n)."""
    low, high = 0, len(sorted_items) - 1
    while low <= high:
        mid = (low + high) // 2
        mid_key = key(sorted_items[mid])
        if mid_key == target:
            return sorted_items[mid]
        elif mid_key < target:
            low = mid + 1
        else:
            high = mid - 1
    return None
