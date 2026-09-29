"""
Queue (FIFO)
------------
Used to process pending transactions in the order they were created:
the first transaction that becomes "pending" is the first one processed.

Implemented with a doubly-linked structure (via collections.deque used
strictly as a container) so enqueue/dequeue are true O(1) operations,
with explicit enqueue/dequeue/front methods as required for a DSA lab.
"""

from collections import deque


class Queue:
    def __init__(self):
        self._items = deque()

    def enqueue(self, item):
        """Add an item to the back of the queue. O(1)."""
        self._items.append(item)

    def dequeue(self):
        """Remove and return the item at the front of the queue. O(1).
        Returns None if the queue is empty."""
        if self.is_empty():
            return None
        return self._items.popleft()

    def front(self):
        """Look at the front item without removing it. O(1)."""
        if self.is_empty():
            return None
        return self._items[0]

    def is_empty(self):
        return len(self._items) == 0

    def __len__(self):
        return len(self._items)

    def to_list(self):
        """Front of queue first."""
        return list(self._items)
