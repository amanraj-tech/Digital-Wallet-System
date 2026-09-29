"""
Hash Table (separate chaining)
-------------------------------
A from-scratch hash table used for fast key -> value lookup, e.g.:
    user_id     -> User
    wallet_id   -> User
    txn_id      -> Transaction

Collisions are resolved with separate chaining (a bucket is a list of
(key, value) pairs). The table resizes itself once it gets too full so
average-case operations stay close to O(1).
"""


class HashTable:
    def __init__(self, capacity=16):
        self._capacity = capacity
        self._size = 0
        self._buckets = [[] for _ in range(self._capacity)]
        self._load_factor_limit = 0.7

    # ---------- internals ----------
    def _hash(self, key):
        """Simple, deterministic hash: Python's built-in hash() folded into
        the current number of buckets."""
        return hash(str(key)) % self._capacity

    def _resize(self):
        old_buckets = self._buckets
        self._capacity *= 2
        self._buckets = [[] for _ in range(self._capacity)]
        self._size = 0
        for bucket in old_buckets:
            for key, value in bucket:
                self.insert(key, value)

    # ---------- Insert ----------
    def insert(self, key, value):
        """Insert or update a key -> value pair. Average O(1)."""
        if (self._size + 1) / self._capacity > self._load_factor_limit:
            self._resize()
        index = self._hash(key)
        bucket = self._buckets[index]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                bucket[i] = (key, value)
                return
        bucket.append((key, value))
        self._size += 1

    # alias, some call sites read better as set()
    set = insert

    # ---------- Search ----------
    def search(self, key):
        """Return the value for `key`, or None if not present. Average O(1)."""
        index = self._hash(key)
        bucket = self._buckets[index]
        for k, v in bucket:
            if k == key:
                return v
        return None

    get = search

    def contains(self, key):
        return self.search(key) is not None

    # ---------- Delete ----------
    def delete(self, key):
        """Remove a key. Returns True if it was present. Average O(1)."""
        index = self._hash(key)
        bucket = self._buckets[index]
        for i, (k, _) in enumerate(bucket):
            if k == key:
                del bucket[i]
                self._size -= 1
                return True
        return False

    def keys(self):
        return [k for bucket in self._buckets for k, _ in bucket]

    def values(self):
        return [v for bucket in self._buckets for _, v in bucket]

    def items(self):
        return [(k, v) for bucket in self._buckets for k, v in bucket]

    def __len__(self):
        return self._size
