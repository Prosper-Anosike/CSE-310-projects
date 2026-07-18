"""
user_service.py

All CRUD operations on the "users" collection.
"""

from firebase_admin import firestore
from database import USERS_COLLECTION


def create_user(db, name, email):
    """
    Create a new user document.

    Validates that name and email are non-empty and that email looks
    like an email address, then writes the document and returns its
    auto-generated Firestore document id.
    """
    name = (name or "").strip()
    email = (email or "").strip()

    if not name:
        raise ValueError("Name cannot be empty.")
    if "@" not in email or not email:
        raise ValueError("Email must be a valid email address.")

    user_data = {
        "name": name,
        "email": email,
        "created_at": firestore.SERVER_TIMESTAMP,
    }

    # add() creates a new document with an auto-generated id and
    # returns (write_result, doc_ref); we only need the doc reference.
    _, doc_ref = db.collection(USERS_COLLECTION).add(user_data)
    return doc_ref.id


def get_users(db):
    """
    Return a list of all users as dictionaries, each including its
    Firestore document id under the "id" key.
    """
    users = []
    for doc in db.collection(USERS_COLLECTION).stream():
        user = doc.to_dict()
        user["id"] = doc.id
        users.append(user)
    return users


def get_user_by_id(db, user_id):
    """
    Fetch a single user by document id.

    Returns the user dict (with "id" included) if found, otherwise
    None. Used to validate that a transaction's user_id points to a
    real user before the transaction is created.
    """
    doc = db.collection(USERS_COLLECTION).document(user_id).get()
    if not doc.exists:
        return None
    user = doc.to_dict()
    user["id"] = doc.id
    return user


def update_user(db, user_id, name=None, email=None):
    """
    Update one or more fields of an existing user.

    Only the fields explicitly provided (not None) are written, so
    callers can update just the name, just the email, or both.
    """
    updates = {}
    if name is not None:
        name = name.strip()
        if not name:
            raise ValueError("Name cannot be empty.")
        updates["name"] = name
    if email is not None:
        email = email.strip()
        if "@" not in email or not email:
            raise ValueError("Email must be a valid email address.")
        updates["email"] = email

    if not updates:
        raise ValueError("No fields provided to update.")

    doc_ref = db.collection(USERS_COLLECTION).document(user_id)
    if not doc_ref.get().exists:
        raise ValueError(f"No user found with id '{user_id}'.")

    doc_ref.update(updates)


def delete_user(db, user_id):
    """
    Delete a user document by id.

    Note: this does not cascade-delete that user's transactions, so
    any existing transactions will keep a user_id that no longer
    resolves to a user document.
    """
    doc_ref = db.collection(USERS_COLLECTION).document(user_id)
    if not doc_ref.get().exists:
        raise ValueError(f"No user found with id '{user_id}'.")
    doc_ref.delete()
