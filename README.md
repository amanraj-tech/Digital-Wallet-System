# Digital Wallet System

A simulated digital wallet application built as a **Data Structures and Algorithms (DSA) Lab
Project**. It demonstrates how core DSA concepts — Linked List, Stack, Queue, Hash Table, Sorting,
and Searching — can power a real, working web application instead of existing only on paper.

**SID:** 2550700
**Presented by:** Aman Raj
**Presented to:** Samali Ghosh

---

## Overview

The system simulates everything a real digital wallet needs: user registration and PIN-secured
login, adding/withdrawing money, sending and receiving funds between wallets, a full transaction
history with search and sort, an undo mechanism, pending-transaction processing, contacts,
notifications, and live analytics — all backed by hand-written data structures rather than
built-in library shortcuts or a database.

## Tech Stack

- **Backend:** Python (Flask) — REST API, in-memory data store
- **Frontend:** HTML, CSS, JavaScript — multi-page web interface

No external database or payment gateway is used. All data lives in memory for the duration of the
session, in line with the scope of a lab project.

## How to Run

```bash
cd backend
pip install -r requirements.txt
python3 app.py
```

Open **http://127.0.0.1:5000** in a browser. Three demo accounts are pre-seeded:

| Email               | PIN  |
|---------------------|------|
| alice@example.com   | 1111 |
| bob@example.com     | 2222 |
| carol@example.com   | 3333 |

Restarting the server resets all data back to these seeded accounts.

## Project Structure

```
backend/
  app.py            Flask routes: pages + JSON API
  store.py          Business logic, wired to the DSA structures below
  models.py         Plain data classes: User, Transaction, Contact, Notification
  seed.py           Demo data
  dsa/
    linked_list.py  Singly linked list  -> transaction history
    stack.py        Stack               -> undo / reverse last transaction
    queue.py        Queue               -> pending transaction processing (FIFO)
    hash_table.py   Hash table          -> user/wallet/transaction lookup
    sorting.py      Insertion / Merge / Quick sort -> sort transactions
    searching.py    Linear & Binary search -> search transactions/users
  templates/        Server-rendered HTML pages (Jinja2)
  static/css        Design system stylesheet
  static/js         Frontend logic (fetch calls to the API)
```

## Where Each DSA Concept Lives

| Concept | Role in the System | Key Point |
|---|---|---|
| **Linked List** | Transaction history per user (`dsa/linked_list.py`) | New transactions inserted at the head → O(1), history stays newest-first |
| **Stack** | Undo / reverse the last transaction (`dsa/stack.py`) | Reversible transactions pushed on completion; undo pops the most recent one (LIFO) |
| **Queue** | Pending transaction processing (`dsa/queue.py`) | Strict FIFO — enqueue when marked pending, dequeue when processed |
| **Hash Table** | User ID / Wallet ID / Transaction ID lookup (`dsa/hash_table.py`) | Custom table with separate chaining, auto-resizing, O(1) average lookup |
| **Sorting** | Sorting transaction records (`dsa/sorting.py`) | Insertion Sort, Merge Sort, and Quick Sort implemented from scratch |
| **Searching** | Searching users, contacts, and transactions (`dsa/searching.py`) | Linear Search for multi-field queries; Binary Search for exact-match lookups |

## Key Features

- User registration, login, and PIN-secured transactions
- Add / withdraw money, send / receive money between wallets
- Complete transaction history with search, sort, and filter
- Undo last transaction, pending transaction queue
- Contacts, notifications, and live analytics (totals, averages, largest transaction)
- Input validation: insufficient balance, invalid amounts, duplicate accounts, self-transfers

## Challenges Faced

1. **Keeping undo consistent with the transaction history** — popping the stack could drift from
   what the linked list showed. Solved by storing a direct reference to the exact transaction node
   in each stack entry, so undo always touches precisely the record it reverses.
2. **Designing an efficient hash function** — a naive hash clustered IDs into a few buckets.
   Solved with a polynomial rolling hash over the ID string, a prime table size, separate chaining,
   and automatic resizing once the load factor gets too high.

## Notes

This is a lab/demo project: PINs are stored in plain text and the Flask session uses a hardcoded
secret key, which is acceptable for a local, in-memory simulation but would need hashing and proper
secret management in a production system. There is intentionally no real payment gateway or banking
API integration, per the project brief.
