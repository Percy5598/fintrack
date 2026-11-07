
import sqlite3
from pathlib import Path

from fintrack.models import Transaction


# Project root directory
BASE_DIR = Path(__file__).resolve().parents[2]

# Database location
DATABASE_PATH = BASE_DIR / "data" / "fintrack.db"


def get_connection():
    """
    Create a connection to the SQLite database.

    Row factory allows us to access columns by name.
    """

    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    # Enforce foreign key constraints.
    connection.execute("PRAGMA foreign_keys = ON")

    return connection


def initialize_database():
    """
    Create the transactions table if it does not exist.
    """

    with get_connection() as connection:

        connection.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,

                transaction_date TEXT NOT NULL,

                description TEXT NOT NULL,

                category TEXT NOT NULL,

                transaction_type TEXT NOT NULL
                    CHECK (transaction_type IN ('income', 'expense')),

                gross_cents INTEGER NOT NULL
                    CHECK (gross_cents > 0),

                vat_rate TEXT NOT NULL,

                vat_deductible INTEGER NOT NULL DEFAULT 0
                    CHECK (vat_deductible IN (0, 1)),

                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_transactions_date
            ON transactions(transaction_date)
        """)

        connection.execute("""
            CREATE INDEX IF NOT EXISTS
            idx_transactions_type
            ON transactions(transaction_type)
        """)


def add_transaction(transaction: Transaction) -> int:
    """
    Insert a transaction into the database.

    Returns:
        The ID of the newly created transaction.
    """

    with get_connection() as connection:

        cursor = connection.execute("""
            INSERT INTO transactions (
                transaction_date,
                description,
                category,
                transaction_type,
                gross_cents,
                vat_rate,
                vat_deductible
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            transaction.transaction_date.isoformat(),
            transaction.description,
            transaction.category,
            transaction.transaction_type,
            transaction.gross_cents,
            str(transaction.vat_rate),
            int(transaction.vat_deductible),
        ))

        return cursor.lastrowid


def get_transactions():
    """
    Retrieve all transactions.

    Returns:
        A list of dictionaries ordered by date.
    """

    with get_connection() as connection:

        cursor = connection.execute("""
            SELECT
                id,
                transaction_date,
                description,
                category,
                transaction_type,
                gross_cents,
                vat_rate,
                vat_deductible,
                created_at
            FROM transactions
            ORDER BY transaction_date DESC, id DESC
        """)

        return [dict(row) for row in cursor.fetchall()]


def get_transaction_by_id(transaction_id: int):
    """Retrieve one transaction by its ID."""

    with get_connection() as connection:

        cursor = connection.execute("""
            SELECT *
            FROM transactions
            WHERE id = ?
        """, (transaction_id,))

        row = cursor.fetchone()

        return dict(row) if row else None


def delete_transaction(transaction_id: int) -> bool:
    """
    Delete a transaction.

    Returns:
        True if a record was deleted, otherwise False.
    """

    with get_connection() as connection:

        cursor = connection.execute("""
            DELETE FROM transactions
            WHERE id = ?
        """, (transaction_id,))

        return cursor.rowcount > 0


def get_transaction_count() -> int:
    """Return the total number of transactions."""

    with get_connection() as connection:

        cursor = connection.execute("""
            SELECT COUNT(*) AS total
            FROM transactions
        """)

        return cursor.fetchone()["total"]
