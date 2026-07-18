"""
transaction_service.py

All CRUD operations on the "transactions" collection, plus the
income/expense/balance calculations that read from it.
"""

from firebase_admin import firestore
from google.cloud.firestore_v1.base_query import FieldFilter
from database import TRANSACTIONS_COLLECTION
from user_service import get_user_by_id

VALID_TRANSACTION_TYPES = {"income", "expense"}


def add_transaction(db, user_id, type_, amount, category, description):
    """
    Create a new transaction linked to an existing user.

    Validates the transaction type, amount, category and description,
    and confirms user_id refers to a real user before writing the
    document, since Firestore has no built-in foreign-key constraint.
    """
    if type_ not in VALID_TRANSACTION_TYPES:
        raise ValueError(f"Type must be one of {VALID_TRANSACTION_TYPES}.")

    try:
        amount = float(amount)
    except (TypeError, ValueError):
        raise ValueError("Amount must be a number.")
    if amount <= 0:
        raise ValueError("Amount must be greater than zero.")

    category = (category or "").strip()
    description = (description or "").strip()
    if not category:
        raise ValueError("Category cannot be empty.")
    if not description:
        raise ValueError("Description cannot be empty.")

    if get_user_by_id(db, user_id) is None:
        raise ValueError(f"No user found with id '{user_id}'.")

    transaction_data = {
        "user_id": user_id,
        "type": type_,
        "amount": amount,
        "category": category,
        "description": description,
        "created_at": firestore.SERVER_TIMESTAMP,
    }

    _, doc_ref = db.collection(TRANSACTIONS_COLLECTION).add(transaction_data)
    return doc_ref.id


def get_transactions(db, user_id=None):
    """
    Return transactions as a list of dictionaries (each including its
    document id under "id").

    If user_id is given, the query is filtered to that user's
    transactions on the server side; otherwise every transaction is
    returned. Results are sorted by creation time client-side, which
    avoids needing a Firestore composite index for the combined
    filter + order-by query.
    """
    query = db.collection(TRANSACTIONS_COLLECTION)
    if user_id is not None:
        query = query.where(filter=FieldFilter("user_id", "==", user_id))

    transactions = []
    for doc in query.stream():
        transaction = doc.to_dict()
        transaction["id"] = doc.id
        transactions.append(transaction)

    # Sort oldest-first; a just-written SERVER_TIMESTAMP can briefly
    # read back as None, so treat missing timestamps as oldest.
    transactions.sort(key=lambda txn: (txn.get("created_at") is not None, txn.get("created_at")))
    return transactions


def update_transaction(db, transaction_id, amount=None, category=None, description=None):
    """
    Update one or more fields of an existing transaction.

    Only amount, category, and description may be changed here; the
    user_id and type of a transaction are treated as immutable once
    created to keep the data model simple and consistent.
    """
    updates = {}
    if amount is not None:
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            raise ValueError("Amount must be a number.")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")
        updates["amount"] = amount
    if category is not None:
        category = category.strip()
        if not category:
            raise ValueError("Category cannot be empty.")
        updates["category"] = category
    if description is not None:
        description = description.strip()
        if not description:
            raise ValueError("Description cannot be empty.")
        updates["description"] = description

    if not updates:
        raise ValueError("No fields provided to update.")

    doc_ref = db.collection(TRANSACTIONS_COLLECTION).document(transaction_id)
    if not doc_ref.get().exists:
        raise ValueError(f"No transaction found with id '{transaction_id}'.")

    doc_ref.update(updates)


def delete_transaction(db, transaction_id):
    """Delete a transaction document by id."""
    doc_ref = db.collection(TRANSACTIONS_COLLECTION).document(transaction_id)
    if not doc_ref.get().exists:
        raise ValueError(f"No transaction found with id '{transaction_id}'.")
    doc_ref.delete()


def calculate_total_income(db, user_id=None):
    """
    Sum the amount of every "income" transaction, optionally scoped
    to a single user. Firestore has no built-in sum aggregation at
    this scope, so the total is summed client-side over the query
    results.
    """
    query = db.collection(TRANSACTIONS_COLLECTION).where(
        filter=FieldFilter("type", "==", "income")
    )
    if user_id is not None:
        query = query.where(filter=FieldFilter("user_id", "==", user_id))
    return sum(doc.to_dict().get("amount", 0) for doc in query.stream())


def calculate_total_expenses(db, user_id=None):
    """
    Sum the amount of every "expense" transaction, optionally scoped
    to a single user.
    """
    query = db.collection(TRANSACTIONS_COLLECTION).where(
        filter=FieldFilter("type", "==", "expense")
    )
    if user_id is not None:
        query = query.where(filter=FieldFilter("user_id", "==", user_id))
    return sum(doc.to_dict().get("amount", 0) for doc in query.stream())


def calculate_balance(db, user_id=None):
    """
    Return total income minus total expenses, optionally scoped to a
    single user (a positive balance means income exceeds expenses).
    """
    income = calculate_total_income(db, user_id)
    expenses = calculate_total_expenses(db, user_id)
    return income - expenses
