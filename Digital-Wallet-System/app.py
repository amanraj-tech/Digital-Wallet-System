"""
Digital Wallet System - Flask backend.

Serves:
  - The multi-page HTML/CSS/JS frontend (templates/ + static/)
  - A JSON REST API under /api/* that the frontend calls with fetch()

All application data lives in memory in a single WalletStore instance
(store.py), which itself is built entirely on the custom DSA structures
in dsa/ (linked list, stack, queue, hash table) plus the sorting and
searching algorithms in dsa/sorting.py and dsa/searching.py.
"""

from functools import wraps

from flask import Flask, render_template, request, jsonify, session

from store import WalletStore, WalletError
from seed import seed_demo_data

app = Flask(__name__)
app.secret_key = "dsa-lab-digital-wallet-secret"  # fine for a local lab demo

store = WalletStore()
seed_demo_data(store)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            return jsonify({"ok": False, "error": "Not logged in."}), 401
        return view(*args, **kwargs)
    return wrapped


def api_ok(data=None, **extra):
    payload = {"ok": True}
    if data is not None:
        payload["data"] = data
    payload.update(extra)
    return jsonify(payload)


def api_error(message, code=400):
    return jsonify({"ok": False, "error": message}), code


@app.errorhandler(WalletError)
def handle_wallet_error(err):
    return api_error(str(err))


# ---------------------------------------------------------------------
# Page routes (multi-page frontend)
# ---------------------------------------------------------------------
@app.route("/")
def page_login():
    return render_template("login.html")


@app.route("/register")
def page_register():
    return render_template("register.html")


@app.route("/dashboard")
def page_dashboard():
    return render_template("dashboard.html")


@app.route("/send")
def page_send():
    return render_template("send.html")


@app.route("/history")
def page_history():
    return render_template("history.html")


@app.route("/contacts")
def page_contacts():
    return render_template("contacts.html")


@app.route("/notifications")
def page_notifications():
    return render_template("notifications.html")


@app.route("/analytics")
def page_analytics():
    return render_template("analytics.html")


@app.route("/pending")
def page_pending():
    return render_template("pending.html")


@app.route("/receipt/<transaction_id>")
def page_receipt(transaction_id):
    return render_template("receipt.html", transaction_id=transaction_id)


# ---------------------------------------------------------------------
# Auth API
# ---------------------------------------------------------------------
@app.post("/api/register")
def api_register():
    body = request.get_json(force=True)
    user = store.register(
        name=body.get("name", "").strip(),
        email=body.get("email", "").strip().lower(),
        phone=body.get("phone", "").strip(),
        pin=body.get("pin", "").strip(),
    )
    session["user_id"] = user.user_id
    return api_ok(user.public_dict())


@app.post("/api/login")
def api_login():
    body = request.get_json(force=True)
    user = store.login(body.get("email", "").strip().lower(), body.get("pin", "").strip())
    session["user_id"] = user.user_id
    return api_ok(user.public_dict())


@app.post("/api/logout")
def api_logout():
    session.clear()
    return api_ok()


@app.get("/api/me")
@login_required
def api_me():
    user = store.get_user(session["user_id"])
    return api_ok(user.public_dict())


# ---------------------------------------------------------------------
# Wallet API
# ---------------------------------------------------------------------
@app.post("/api/wallet/add")
@login_required
def api_add_money():
    body = request.get_json(force=True)
    txn = store.add_money(session["user_id"], body.get("amount"), body.get("description", "Added via top-up"))
    user = store.get_user(session["user_id"])
    return api_ok({"transaction": txn.public_dict(), "balance": round(user.balance, 2)})


@app.post("/api/wallet/withdraw")
@login_required
def api_withdraw_money():
    body = request.get_json(force=True)
    txn = store.withdraw_money(session["user_id"], body.get("amount"), body.get("description", "Withdrawal"))
    user = store.get_user(session["user_id"])
    return api_ok({"transaction": txn.public_dict(), "balance": round(user.balance, 2)})


# ---------------------------------------------------------------------
# Send money API
# ---------------------------------------------------------------------
@app.post("/api/send")
@login_required
def api_send_money():
    body = request.get_json(force=True)
    txn = store.send_money(
        sender_id=session["user_id"],
        receiver_identifier=body.get("receiver", "").strip(),
        amount=body.get("amount"),
        pin=body.get("pin", "").strip(),
        description=body.get("description", ""),
    )
    user = store.get_user(session["user_id"])
    return api_ok({"transaction": txn.public_dict(), "balance": round(user.balance, 2)})


# ---------------------------------------------------------------------
# Undo API
# ---------------------------------------------------------------------
@app.post("/api/undo")
@login_required
def api_undo():
    txn = store.undo_last_transaction(session["user_id"])
    user = store.get_user(session["user_id"])
    return api_ok({"transaction": txn.public_dict(), "balance": round(user.balance, 2)})


# ---------------------------------------------------------------------
# Pending transaction API (Queue)
# ---------------------------------------------------------------------
@app.get("/api/pending")
@login_required
def api_list_pending():
    items = store.list_pending(session["user_id"])
    return api_ok([t.public_dict() for t in items])


@app.post("/api/pending/process")
@login_required
def api_process_pending():
    txn = store.process_next_pending(session["user_id"])
    user = store.get_user(session["user_id"])
    return api_ok({"transaction": txn.public_dict(), "balance": round(user.balance, 2)})


# ---------------------------------------------------------------------
# Transaction history / search / sort API
# ---------------------------------------------------------------------
@app.get("/api/transactions")
@login_required
def api_transactions():
    limit = request.args.get("limit", type=int)
    items = store.get_history(session["user_id"], limit=limit)
    return api_ok([t.public_dict() for t in items])


@app.get("/api/transactions/search")
@login_required
def api_transactions_search():
    field = request.args.get("field", "")
    query = request.args.get("query", "")
    items = store.search_transactions(session["user_id"], field, query)
    return api_ok([t.public_dict() for t in items])


@app.get("/api/transactions/sort")
@login_required
def api_transactions_sort():
    sort_by = request.args.get("sort_by", "newest_first")
    algorithm = request.args.get("algorithm", "merge")
    items = store.sort_transactions(session["user_id"], sort_by, algorithm)
    return api_ok([t.public_dict() for t in items])


@app.get("/api/receipt/<transaction_id>")
@login_required
def api_receipt(transaction_id):
    txn = store.get_transaction(transaction_id)
    return api_ok(txn.public_dict())


# ---------------------------------------------------------------------
# User / wallet search API
# ---------------------------------------------------------------------
@app.get("/api/users/search")
@login_required
def api_search_users():
    query = request.args.get("query", "")
    users = store.search_users(query)
    me = session["user_id"]
    return api_ok([u.public_dict() for u in users if u.user_id != me])


# ---------------------------------------------------------------------
# Contacts API
# ---------------------------------------------------------------------
@app.get("/api/contacts")
@login_required
def api_list_contacts():
    contacts = store.list_contacts(session["user_id"])
    return api_ok([c.public_dict() for c in contacts])


@app.post("/api/contacts/add")
@login_required
def api_add_contact():
    body = request.get_json(force=True)
    contact = store.add_contact(session["user_id"], body.get("identifier", "").strip())
    return api_ok(contact.public_dict())


@app.post("/api/contacts/remove")
@login_required
def api_remove_contact():
    body = request.get_json(force=True)
    store.remove_contact(session["user_id"], body.get("contact_id"))
    return api_ok()


@app.get("/api/contacts/search")
@login_required
def api_search_contacts():
    query = request.args.get("query", "")
    contacts = store.search_contacts(session["user_id"], query)
    return api_ok([c.public_dict() for c in contacts])


# ---------------------------------------------------------------------
# Notifications API
# ---------------------------------------------------------------------
@app.get("/api/notifications")
@login_required
def api_list_notifications():
    items = store.list_notifications(session["user_id"])
    return api_ok([n.public_dict() for n in items])


@app.post("/api/notifications/read")
@login_required
def api_read_notification():
    body = request.get_json(force=True)
    note = store.mark_notification_read(session["user_id"], body.get("notification_id"))
    return api_ok(note.public_dict())


# ---------------------------------------------------------------------
# Analytics API
# ---------------------------------------------------------------------
@app.get("/api/analytics")
@login_required
def api_analytics():
    return api_ok(store.get_analytics(session["user_id"]))


if __name__ == "__main__":
    app.run(debug=True, port=5000)
