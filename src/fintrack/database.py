import sqlite3
from pathlib import Path

from fintrack.models import Transaction


DATABASE_PATH = Path("data/fintrack.db")


def get_connection() -> sqlite3.Connection:
    """Create a connection to the application database."""
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database() -> None:
    """Create the transactions table if it does not exist."""
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transaction_date TEXT NOT NULL,
                description TEXT NOT NULL,
                category TEXT NOT NULL,
                transaction_type TEXT NOT NULL
                    CHECK (transaction_type IN ('income', 'expense')),
                gross_cents INTEGER NOT NULL CHECK (gross_cents >= 0),
                vat_rate TEXT NOT NULL,
                vat_deductible INTEGER NOT NULL DEFAULT 1
            )
            """
        )


def add_transaction(transaction: Transaction) -> int:
    """Save a transaction and return its database ID."""
    with get_connection() as connection:
        cursor = connection.execute(
            """
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
            """,
            (
                transaction.transaction_date.isoformat(),
                transaction.description,
                transaction.category,
                transaction.transaction_type,
                transaction.gross_cents,
                str(transaction.vat_rate),
                int(transaction.vat_deductible),
            ),
        )

        return cursor.lastrowid


def get_transactions() -> list[dict]:
    """Return all transactions, newest first."""
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT *
            FROM transactions
            ORDER BY transaction_date DESC, id DESC
            """
        ).fetchall()

    return [dict(row) for row in rows]


def delete_transaction(transaction_id: int) -> None:
    """Delete a transaction by its database ID."""
    with get_connection() as connection:
        connection.execute(
            "DELETE FROM transactions WHERE id = ?",
            (transaction_id,),
        )