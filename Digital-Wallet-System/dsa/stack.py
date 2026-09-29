"""
Stack (LIFO)
------------
Used to track a user's most recent reversible operations so the newest
one can be undone first.

Implemented on top of a plain Python list ONLY as the underlying storage
array (push/pop/peek are re-implemented explicitly so the LIFO behaviour
is explicit and documented, as required for a DSA lab).
"""


class Stack:
    def __init__(self, max_size=None):
        self._items = []
        self.max_size = max_size

    def push(self, item):
        """Add an item to the top of the stack. O(1)."""
        if self.max_size is not None and len(self._items) >= self.max_size:
            # Drop the oldest reversible action to keep the stack bounded
            self._items.pop(0)
        self._items.append(item)

    def pop(self):
        """Remove and return the top item. O(1). Returns None if empty."""
        if self.is_empty():
            return None
        return self._items.pop()

    def peek(self):
        """Look at the top item without removing it. O(1)."""
        if self.is_empty():
            return None
        return self._items[-1]

    def is_empty(self):
        return len(self._items) == 0

    def __len__(self):
        return len(self._items)

    def to_list(self):
        """Top of stack first."""
        return list(reversed(self._items))
