"""Seed a few demo users and sample transactions so the app can be
explored immediately without registering from scratch first."""


def seed_demo_data(store):
    alice = store.register("demo", "alice@example.com", "9990000001", "1111")
    bob = store.register("demo", "bob@example.com", "9990000002", "2222")
    carol = store.register("demo", "carol@example.com", "9990000003", "3333")

    store.add_money(alice.user_id, 5000, "Initial top-up")
    store.add_money(bob.user_id, 2000, "Initial top-up")
    store.add_money(carol.user_id, 1000, "Initial top-up")

    store.send_money(alice.user_id, bob.wallet_id, 500, "1111", "Lunch split")
    store.send_money(bob.user_id, carol.wallet_id, 200, "2222", "Movie tickets")
    store.withdraw_money(alice.user_id, 300, "ATM withdrawal")

    store.add_contact(alice.user_id, bob.wallet_id)
    store.add_contact(alice.user_id, carol.wallet_id)
    store.add_contact(bob.user_id, alice.wallet_id)

    # A couple of pending transactions to demonstrate the Queue feature
    from models import Transaction
    pending_txn = Transaction(sender=alice, receiver=carol, amount=150,
                               txn_type="Money Sent", description="Pending settlement")
    store.queue_pending(alice.user_id, pending_txn)
