"""
WalletStore
-----------
The application's in-memory "database" and business logic layer.

Three hash tables give O(1) average lookup by user id, wallet id, and
transaction id (requirement: Hash Table for user/wallet/transaction lookup).
Everything else (history, undo, pending processing, sorting, searching)
delegates to the DSA structures defined in dsa/.
"""

from datetime import datetime

from dsa.hash_table import HashTable
from dsa.sorting import SORT_ALGORITHMS
from dsa.searching import linear_search, binary_search
from models import User, Transaction, Contact, Notification


class WalletError(Exception):
    """Raised for any validation / business-rule failure. The API layer
    turns these into clean JSON error responses."""


class WalletStore:
    def __init__(self):
        self.users_by_id = HashTable()
        self.users_by_wallet = HashTable()
        self.users_by_email = HashTable()
        self.users_by_phone = HashTable()
        self.transactions_by_id = HashTable()

    # ------------------------------------------------------------------
    # Authentication / registration
    # ------------------------------------------------------------------
    def register(self, name, email, phone, pin):
        if not name or not email or not phone or not pin:
            raise WalletError("All fields (name, email, phone, PIN) are required.")
        if self.users_by_email.contains(email):
            raise WalletError("An account with this email already exists.")
        if self.users_by_phone.contains(phone):
            raise WalletError("An account with this phone number already exists.")
        if not (isinstance(pin, str) and pin.isdigit() and len(pin) == 4):
            raise WalletError("PIN must be exactly 4 digits.")

        user = User(name=name, email=email, phone=phone, pin=pin)
        self.users_by_id.insert(user.user_id, user)
        self.users_by_wallet.insert(user.wallet_id, user)
        self.users_by_email.insert(email, user)
        self.users_by_phone.insert(phone, user)
        self._notify(user, f"Welcome {user.name}! Your wallet {user.wallet_id} is ready.")
        return user

    def login(self, email, pin):
        user = self.users_by_email.search(email)
        if user is None or not user.verify_pin(pin):
            raise WalletError("Invalid email or PIN.")
        return user

    def get_user(self, user_id):
        user = self.users_by_id.search(user_id)
        if user is None:
            raise WalletError("User not found.")
        return user

    # ------------------------------------------------------------------
    # Wallet management
    # ------------------------------------------------------------------
    def add_money(self, user_id, amount, description="Added via top-up"):
        amount = self._validate_amount(amount)
        user = self.get_user(user_id)
        user.balance += amount
        txn = Transaction(sender=None, receiver=user, amount=amount,
                           txn_type="Money Added", description=description)
        self._record_transaction(user, txn)
        self._notify(user, f"₹{amount:.2f} added to your wallet.")
        return txn

    def withdraw_money(self, user_id, amount, description="Withdrawal"):
        amount = self._validate_amount(amount)
        user = self.get_user(user_id)
        if amount > user.balance:
            txn = Transaction(sender=user, receiver=None, amount=amount,
                               txn_type="Money Withdrawn", description=description,
                               status="Failed")
            self._record_transaction(user, txn, push_undo=False)
            self._notify(user, f"Withdrawal of ₹{amount:.2f} failed: insufficient balance.")
            raise WalletError("Insufficient balance for this withdrawal.")
        user.balance -= amount
        txn = Transaction(sender=user, receiver=None, amount=amount,
                           txn_type="Money Withdrawn", description=description)
        self._record_transaction(user, txn)
        self._notify(user, f"₹{amount:.2f} withdrawn from your wallet.")
        return txn

    # ------------------------------------------------------------------
    # Send / receive money
    # ------------------------------------------------------------------
    def send_money(self, sender_id, receiver_identifier, amount, pin, description=""):
        amount = self._validate_amount(amount)
        sender = self.get_user(sender_id)

        if not sender.verify_pin(pin):
            raise WalletError("Incorrect PIN.")

        receiver = self.find_user(receiver_identifier)
        if receiver is None:
            raise WalletError("Receiver not found.")
        if receiver.user_id == sender.user_id:
            raise WalletError("You cannot send money to your own account.")
        if amount > sender.balance:
            txn = Transaction(sender=sender, receiver=receiver, amount=amount,
                               txn_type="Money Sent", description=description,
                               status="Failed")
            self._record_transaction(sender, txn, push_undo=False)
            self._notify(sender, f"Transfer of ₹{amount:.2f} to {receiver.name} failed: insufficient balance.")
            raise WalletError("Insufficient balance for this transfer.")

        # Perform the transfer
        sender.balance -= amount
        receiver.balance += amount

        sent_txn = Transaction(sender=sender, receiver=receiver, amount=amount,
                                txn_type="Money Sent", description=description)
        received_txn = Transaction(sender=sender, receiver=receiver, amount=amount,
                                    txn_type="Money Received", description=description)

        self._record_transaction(sender, sent_txn)
        self._record_transaction(receiver, received_txn, push_undo=False)

        self._notify(sender, f"₹{amount:.2f} sent to {receiver.name}.")
        self._notify(receiver, f"₹{amount:.2f} received from {sender.name}.")
        return sent_txn

    # ------------------------------------------------------------------
    # Undo / reverse (Stack)
    # ------------------------------------------------------------------
    def undo_last_transaction(self, user_id):
        user = self.get_user(user_id)
        txn = user.undo_stack.pop()
        if txn is None:
            raise WalletError("Nothing to undo.")
        if txn.status == "Reversed":
            raise WalletError("This transaction was already reversed.")

        if txn.type == "Money Added":
            user.balance -= txn.amount
        elif txn.type == "Money Withdrawn":
            user.balance += txn.amount
        elif txn.type == "Money Sent":
            receiver = self.users_by_id.search(txn.receiver_id)
            user.balance += txn.amount
            if receiver:
                receiver.balance -= txn.amount
                self._notify(receiver, f"A transfer of ₹{txn.amount:.2f} from {user.name} was reversed.")

        txn.status = "Reversed"
        self._notify(user, f"Transaction {txn.transaction_id} was reversed.")
        return txn

    # ------------------------------------------------------------------
    # Pending transaction processing (Queue)
    # ------------------------------------------------------------------
    def queue_pending(self, user_id, txn):
        user = self.get_user(user_id)
        txn.status = "Pending"
        user.pending_queue.enqueue(txn)
        return txn

    def process_next_pending(self, user_id):
        user = self.get_user(user_id)
        txn = user.pending_queue.dequeue()
        if txn is None:
            raise WalletError("No pending transactions to process.")
        txn.status = "Success"
        self._notify(user, f"Pending transaction {txn.transaction_id} has been processed.")
        return txn

    def list_pending(self, user_id):
        user = self.get_user(user_id)
        return user.pending_queue.to_list()

    # ------------------------------------------------------------------
    # User / wallet search
    # ------------------------------------------------------------------
    def find_user(self, identifier):
        """Search by user id, wallet id, phone, or (case-insensitive) name."""
        user = self.users_by_id.search(identifier)
        if user:
            return user
        user = self.users_by_wallet.search(identifier)
        if user:
            return user
        user = self.users_by_phone.search(identifier)
        if user:
            return user
        matches = linear_search(self.users_by_id.values(),
                                 lambda u: u.name.lower() == str(identifier).lower())
        return matches[0] if matches else None

    def search_users(self, query):
        query = str(query).lower()
        return linear_search(
            self.users_by_id.values(),
            lambda u: query in u.name.lower()
            or query in u.user_id.lower()
            or query in u.wallet_id.lower()
            or query in u.phone.lower(),
        )

    # ------------------------------------------------------------------
    # Transaction history / search / sort
    # ------------------------------------------------------------------
    def get_history(self, user_id, limit=None):
        user = self.get_user(user_id)
        items = user.history.to_list()
        return items[:limit] if limit else items

    def search_transactions(self, user_id, field, query):
        user = self.get_user(user_id)
        items = user.history.to_list()
        query_str = str(query).lower()

        field_map = {
            "transaction_id": lambda t: query_str in t.transaction_id.lower(),
            "sender": lambda t: query_str in (t.sender_name or "").lower(),
            "receiver": lambda t: query_str in (t.receiver_name or "").lower(),
            "amount": lambda t: t.amount == self._safe_float(query),
            "type": lambda t: query_str in t.type.lower(),
            "date": lambda t: t.timestamp.strftime("%Y-%m-%d") == query_str,
        }
        predicate = field_map.get(field)
        if predicate is None:
            raise WalletError(f"Unknown search field '{field}'.")
        return linear_search(items, predicate)

    def sort_transactions(self, user_id, sort_by, algorithm="merge"):
        user = self.get_user(user_id)
        items = user.history.to_list()
        sort_fn = SORT_ALGORITHMS.get(algorithm, SORT_ALGORITHMS["merge"])

        key_map = {
            "amount_low_high": (lambda t: t.amount, False),
            "amount_high_low": (lambda t: t.amount, True),
            "newest_first": (lambda t: t.timestamp, True),
            "oldest_first": (lambda t: t.timestamp, False),
            "sender_receiver_name": (lambda t: (t.sender_name or "").lower(), False),
            "transaction_type": (lambda t: t.type, False),
        }
        key_fn, reverse = key_map.get(sort_by, (lambda t: t.timestamp, True))
        return sort_fn(items, key=key_fn, reverse=reverse)

    def get_transaction(self, transaction_id):
        txn = self.transactions_by_id.search(transaction_id)
        if txn is None:
            raise WalletError("Transaction not found.")
        return txn

    # ------------------------------------------------------------------
    # Contacts
    # ------------------------------------------------------------------
    def add_contact(self, owner_id, contact_identifier):
        owner = self.get_user(owner_id)
        contact_user = self.find_user(contact_identifier)
        if contact_user is None:
            raise WalletError("User to add as contact was not found.")
        if contact_user.user_id == owner.user_id:
            raise WalletError("You cannot add yourself as a contact.")
        for c in owner.contacts.values():
            if c.user_id == contact_user.user_id:
                raise WalletError("This user is already in your contacts.")
        contact = Contact(owner.user_id, contact_user)
        owner.contacts[contact.contact_id] = contact
        return contact

    def remove_contact(self, owner_id, contact_id):
        owner = self.get_user(owner_id)
        if contact_id not in owner.contacts:
            raise WalletError("Contact not found.")
        del owner.contacts[contact_id]

    def search_contacts(self, owner_id, query):
        owner = self.get_user(owner_id)
        query = query.lower()
        return linear_search(
            list(owner.contacts.values()),
            lambda c: query in c.name.lower() or query in c.wallet_id.lower(),
        )

    def list_contacts(self, owner_id):
        owner = self.get_user(owner_id)
        return list(owner.contacts.values())

    # ------------------------------------------------------------------
    # Notifications
    # ------------------------------------------------------------------
    def list_notifications(self, user_id):
        user = self.get_user(user_id)
        return user.notifications

    def mark_notification_read(self, user_id, notification_id):
        user = self.get_user(user_id)
        for n in user.notifications:
            if n.notification_id == notification_id:
                n.read = True
                return n
        raise WalletError("Notification not found.")

    def _notify(self, user, message):
        note = Notification(message)
        user.notifications.insert(0, note)  # newest first
        return note

    # ------------------------------------------------------------------
    # Analytics (derived, not stored)
    # ------------------------------------------------------------------
    def get_analytics(self, user_id):
        user = self.get_user(user_id)
        txns = [t for t in user.history.to_list() if t.status == "Success"]

        def total_for(types):
            return round(sum(t.amount for t in txns if t.type in types), 2)

        amounts = [t.amount for t in txns]
        largest = max(txns, key=lambda t: t.amount) if txns else None

        return {
            "total_received": total_for({"Money Received"}),
            "total_sent": total_for({"Money Sent"}),
            "total_added": total_for({"Money Added"}),
            "total_withdrawn": total_for({"Money Withdrawn"}),
            "number_of_transactions": len(txns),
            "largest_transaction": largest.public_dict() if largest else None,
            "average_transaction_amount": round(sum(amounts) / len(amounts), 2) if amounts else 0.0,
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _record_transaction(self, user, txn, push_undo=True):
        user.history.insert_at_head(txn)
        self.transactions_by_id.insert(txn.transaction_id, txn)
        if push_undo and txn.status == "Success":
            user.undo_stack.push(txn)

    @staticmethod
    def _validate_amount(amount):
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise WalletError("Amount must be a number.")
        if amount <= 0:
            raise WalletError("Amount must be greater than zero.")
        return round(amount, 2)

    @staticmethod
    def _safe_float(value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return None
