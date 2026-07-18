"""
database.py

Central place for shared Firestore access: the cached database client
and the collection name constants used by both service modules.
"""

from firebase_config import initialize_firebase

# Firestore collection names, defined once so a typo can't create a
# second accidental collection somewhere in the codebase.
USERS_COLLECTION = "users"
TRANSACTIONS_COLLECTION = "transactions"


def get_db():
    """
    Return the shared Firestore client.

    This is the single call site for initialize_firebase(); every
    service module should get its client through this function.
    """
    return initialize_firebase()
