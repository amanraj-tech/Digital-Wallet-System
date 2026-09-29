"""
Domain models. Plain data classes -- no DSA logic lives here, only the
shape of the data. The DSA structures (linked list, stack, queue, hash
table) that hold and organize these objects live in store.py.
"""

import uuid
from datetime import datetime


def new_id(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8].upper()}"


class User:
    def __init__(self, name, email, phone, pin):
        self.user_id = new_id("USR")
        self.wallet_id = new_id("WLT")
        self.name = name
        self.email = email
        self.phone = phone
        self.pin = pin  # stored as-is for lab-project simplicity (see README)
        self.balance = 0.0
        self.created_at = datetime.now()

        # Per-user DSA structures (imported lazily to avoid circular import)
        from dsa.linked_list import LinkedList
        from dsa.stack import Stack
        from dsa.queue import Queue

        self.history = LinkedList()          # all transactions, newest first
        self.undo_stack = Stack(max_size=20)  # recent reversible actions
        self.pending_queue = Queue()          # transactions awaiting processing
        self.contacts = {}                    # contact_id -> Contact
        self.notifications = []               # simple reverse-chrono list

    def public_dict(self):
        return {
            "user_id": self.user_id,
            "wallet_id": self.wallet_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "balance": round(self.balance, 2),
            "created_at": self.created_at.isoformat(),
        }

    def verify_pin(self, pin):
        return str(pin) == str(self.pin)


class Transaction:
    def __init__(self, sender, receiver, amount, txn_type, description="", status="Success"):
        self.transaction_id = new_id("TXN")
        self.sender_id = sender.user_id if sender else None
        self.receiver_id = receiver.user_id if receiver else None
        self.sender_name = sender.name if sender else "N/A"
        self.receiver_name = receiver.name if receiver else "N/A"
        self.amount = round(amount, 2)
        self.type = txn_type  # Money Added / Money Withdrawn / Money Sent / Money Received
        self.timestamp = datetime.now()
        self.description = description
        self.status = status  # Success / Failed / Pending / Reversed

    def public_dict(self):
        return {
            "transaction_id": self.transaction_id,
            "sender_id": self.sender_id,
            "receiver_id": self.receiver_id,
            "sender_name": self.sender_name,
            "receiver_name": self.receiver_name,
            "amount": self.amount,
            "type": self.type,
            "date": self.timestamp.strftime("%Y-%m-%d"),
            "time": self.timestamp.strftime("%H:%M:%S"),
            "timestamp": self.timestamp.isoformat(),
            "description": self.description,
            "status": self.status,
        }


class Contact:
    def __init__(self, owner_user_id, contact_user):
        self.contact_id = new_id("CNT")
        self.owner_user_id = owner_user_id
        self.user_id = contact_user.user_id
        self.name = contact_user.name
        self.wallet_id = contact_user.wallet_id

    def public_dict(self):
        return {
            "contact_id": self.contact_id,
            "user_id": self.user_id,
            "name": self.name,
            "wallet_id": self.wallet_id,
        }


class Notification:
    def __init__(self, message):
        self.notification_id = new_id("NTF")
        self.message = message
        self.timestamp = datetime.now()
        self.read = False

    def public_dict(self):
        return {
            "notification_id": self.notification_id,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "read": self.read,
        }
