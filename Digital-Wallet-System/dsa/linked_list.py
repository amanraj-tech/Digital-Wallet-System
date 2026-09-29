"""
Singly Linked List
-------------------
Used to store each user's transaction history in chronological order
(newest transaction is inserted at the head so "recent transactions"
is an O(1) operation).

This is a real, from-scratch linked list (no Python list under the hood)
with the operations a DSA lab expects: insert, delete, traverse, search.
"""


class Node:
    __slots__ = ("data", "next")

    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self._size = 0

    def __len__(self):
        return self._size

    # ---------- Insert ----------
    def insert_at_head(self, data):
        """O(1) insert. New transactions are added here so the list
        is naturally ordered newest -> oldest."""
        node = Node(data)
        node.next = self.head
        self.head = node
        if self.tail is None:
            self.tail = node
        self._size += 1
        return node

    def insert_at_tail(self, data):
        """O(1) insert at the end (kept for completeness / oldest-first use)."""
        node = Node(data)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._size += 1
        return node

    # ---------- Delete ----------
    def delete(self, predicate):
        """Delete the first node whose data matches `predicate(data) -> bool`.
        Returns the removed data or None. O(n)."""
        prev = None
        current = self.head
        while current is not None:
            if predicate(current.data):
                if prev is None:
                    self.head = current.next
                else:
                    prev.next = current.next
                if current is self.tail:
                    self.tail = prev
                self._size -= 1
                return current.data
            prev = current
            current = current.next
        return None

    # ---------- Traverse ----------
    def traverse(self):
        """Generator that yields data from head to tail. O(n)."""
        current = self.head
        while current is not None:
            yield current.data
            current = current.next

    def to_list(self):
        return list(self.traverse())

    # ---------- Search ----------
    def search(self, predicate):
        """Linear search through the linked list. Returns the first match
        or None. O(n) -- demonstrates why a hash table is used elsewhere
        for O(1) lookups."""
        for data in self.traverse():
            if predicate(data):
                return data
        return None

    def search_all(self, predicate):
        return [data for data in self.traverse() if predicate(data)]
