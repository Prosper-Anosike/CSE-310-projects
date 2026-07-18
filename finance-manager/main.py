"""
main.py

Menu-driven command-line interface for the Personal Finance Manager.
Wires together database.py, user_service.py, and transaction_service.py
into an interactive loop that exposes full CRUD functionality.
"""

import database
import user_service
import transaction_service

MENU_TEXT = """
===== Personal Finance Manager =====
 1. Add a new user
 2. Add a new income transaction
 3. Add a new expense transaction
 4. Display all users
 5. Display all transactions
 6. Display transactions for a selected user
 7. Calculate total income
 8. Calculate total expenses
 9. Calculate current balance
10. Update user information
11. Update transaction amount
12. Update transaction category
13. Update transaction description
14. Delete a transaction
15. Delete a user
 0. Exit
======================================
"""


def prompt_nonempty(label):
    """Repeatedly prompt until the user enters a non-empty string."""
    while True:
        value = input(f"{label}: ").strip()
        if value:
            return value
        print("This field cannot be empty. Please try again.")


def prompt_float(label):
    """Repeatedly prompt until the user enters a valid number."""
    while True:
        raw_value = input(f"{label}: ").strip()
        try:
            return float(raw_value)
        except ValueError:
            print("Please enter a valid number.")


def prompt_optional(label):
    """
    Prompt for a value that may be left blank.

    Returns None if the user just presses Enter, signaling "don't
    change this field" to the update_* service functions.
    """
    value = input(f"{label} (leave blank to skip): ").strip()
    return value if value else None


def print_users(users):
    """Print a list of user dictionaries in a readable table-like format."""
    if not users:
        print("No users found.")
        return
    for user in users:
        print(f"ID: {user['id']} | Name: {user['name']} | Email: {user['email']}")


def print_transactions(transactions):
    """Print a list of transaction dictionaries in a readable format."""
    if not transactions:
        print("No transactions found.")
        return
    for txn in transactions:
        print(
            f"ID: {txn['id']} | User: {txn['user_id']} | Type: {txn['type']} | "
            f"Amount: ${txn['amount']:.2f} | Category: {txn['category']} | "
            f"Description: {txn['description']}"
        )


def handle_add_user(db):
    """Prompt for user details and create the user."""
    name = prompt_nonempty("Name")
    email = prompt_nonempty("Email")
    user_id = user_service.create_user(db, name, email)
    print(f"User created with id: {user_id}")


def handle_add_transaction(db, type_):
    """Prompt for transaction details and create an income or expense transaction."""
    user_id = prompt_nonempty("User id")
    amount = prompt_float("Amount")
    category = prompt_nonempty("Category")
    description = prompt_nonempty("Description")
    txn_id = transaction_service.add_transaction(
        db, user_id, type_, amount, category, description
    )
    print(f"{type_.capitalize()} transaction created with id: {txn_id}")


def handle_display_all_users(db):
    """Fetch and display every user."""
    print_users(user_service.get_users(db))


def handle_display_all_transactions(db):
    """Fetch and display every transaction."""
    print_transactions(transaction_service.get_transactions(db))


def handle_display_user_transactions(db):
    """Fetch and display transactions belonging to one selected user."""
    user_id = prompt_nonempty("User id")
    print_transactions(transaction_service.get_transactions(db, user_id))


def handle_calculate_total_income(db):
    """Prompt for an optional user id and display total income."""
    user_id = prompt_optional("User id")
    total = transaction_service.calculate_total_income(db, user_id)
    print(f"Total income: ${total:.2f}")


def handle_calculate_total_expenses(db):
    """Prompt for an optional user id and display total expenses."""
    user_id = prompt_optional("User id")
    total = transaction_service.calculate_total_expenses(db, user_id)
    print(f"Total expenses: ${total:.2f}")


def handle_calculate_balance(db):
    """Prompt for an optional user id and display the current balance."""
    user_id = prompt_optional("User id")
    balance = transaction_service.calculate_balance(db, user_id)
    print(f"Current balance: ${balance:.2f}")


def handle_update_user(db):
    """Prompt for a user id and any fields to change, then apply the update."""
    user_id = prompt_nonempty("User id")
    name = prompt_optional("New name")
    email = prompt_optional("New email")
    user_service.update_user(db, user_id, name=name, email=email)
    print("User updated.")


def handle_update_transaction_field(db, field_name):
    """Prompt for a transaction id and a new value for a single field."""
    transaction_id = prompt_nonempty("Transaction id")
    if field_name == "amount":
        new_value = prompt_float("New amount")
        transaction_service.update_transaction(db, transaction_id, amount=new_value)
    elif field_name == "category":
        new_value = prompt_nonempty("New category")
        transaction_service.update_transaction(db, transaction_id, category=new_value)
    else:
        new_value = prompt_nonempty("New description")
        transaction_service.update_transaction(db, transaction_id, description=new_value)
    print("Transaction updated.")


def handle_delete_transaction(db):
    """Prompt for a transaction id and delete it."""
    transaction_id = prompt_nonempty("Transaction id")
    transaction_service.delete_transaction(db, transaction_id)
    print("Transaction deleted.")


def handle_delete_user(db):
    """Prompt for a user id and delete it."""
    user_id = prompt_nonempty("User id")
    user_service.delete_user(db, user_id)
    print("User deleted.")


# Maps each menu number to the handler that should run for it.
MENU_ACTIONS = {
    "1": handle_add_user,
    "2": lambda db: handle_add_transaction(db, "income"),
    "3": lambda db: handle_add_transaction(db, "expense"),
    "4": handle_display_all_users,
    "5": handle_display_all_transactions,
    "6": handle_display_user_transactions,
    "7": handle_calculate_total_income,
    "8": handle_calculate_total_expenses,
    "9": handle_calculate_balance,
    "10": handle_update_user,
    "11": lambda db: handle_update_transaction_field(db, "amount"),
    "12": lambda db: handle_update_transaction_field(db, "category"),
    "13": lambda db: handle_update_transaction_field(db, "description"),
    "14": handle_delete_transaction,
    "15": handle_delete_user,
}


def main():
    """
    Entry point: connect to Firestore, then run the menu loop until
    the user chooses to exit.
    """
    try:
        db = database.get_db()
        # Quick connectivity check so a missing/invalid service account
        # key fails fast with a clear message instead of failing later
        # inside a random menu option.
        user_service.get_users(db)
    except Exception as error:
        print(f"Failed to connect to Firebase: {error}")
        return

    while True:
        print(MENU_TEXT)
        choice = input("Select an option: ").strip()

        if choice == "0":
            print("Goodbye!")
            break

        action = MENU_ACTIONS.get(choice)
        if action is None:
            print("Invalid option. Please try again.")
            continue

        try:
            action(db)
        except Exception as error:
            print(f"Error: {error}")


if __name__ == "__main__":
    main()
