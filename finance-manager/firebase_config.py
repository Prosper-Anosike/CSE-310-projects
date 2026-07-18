"""
firebase_config.py

Handles Firebase Admin SDK setup. This is the only file that should
touch firebase_admin.initialize_app() or the service account key.
"""

import firebase_admin
from firebase_admin import credentials, firestore

# Path to the downloaded Firebase service account key.
# This file is gitignored and must be supplied by each developer/user.
SERVICE_ACCOUNT_KEY_PATH = "serviceAccountKey.json"

# Module-level cache so the SDK is only initialized once per process.
_firestore_client = None


def initialize_firebase():
    """
    Initialize the Firebase Admin SDK and return a Firestore client.

    Safe to call multiple times: if the app is already initialized
    (or a client was already created), the existing client is reused
    instead of re-initializing the SDK.
    """
    global _firestore_client

    if _firestore_client is not None:
        return _firestore_client

    # Only initialize the default app if it hasn't been created yet,
    # otherwise firebase_admin raises a "default app already exists" error.
    if not firebase_admin._apps:
        try:
            cred = credentials.Certificate(SERVICE_ACCOUNT_KEY_PATH)
            firebase_admin.initialize_app(cred)
        except FileNotFoundError as error:
            raise FileNotFoundError(
                f"Could not find '{SERVICE_ACCOUNT_KEY_PATH}'. Download it from "
                "Firebase Console > Project Settings > Service Accounts and place "
                "it in the finance-manager folder."
            ) from error

    _firestore_client = firestore.client()
    return _firestore_client
