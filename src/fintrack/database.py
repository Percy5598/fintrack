import sqlite3
from datetime import date
from pathlib import Path
from typing import Iterable, List, Optional

from .models import Transaction, TransactionType


class Database:
    def __init__(self, path: str | Path = "data/fintrack.db"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL CHECK (type IN ('income','expense')),
                    category TEXT NOT NULL,
                    description TEXT NOT NULL,
                    amount_net REAL NOT NULL,
                    vat_rate REAL NOT NULL,
                    vat_deductible INTEGER NOT NULL DEFAULT 0,
                    date TEXT NOT NULL,
                    notes TEXT DEFAULT ''
                )
                """
            )

    # --- CRUD ---------------------------------------------------------
    def add(self, t: Transaction) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """INSERT INTO transactions
                   (type, category, description, amount_net, vat_rate,
                    vat_deductible, date, notes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    t.type.value, t.category, t.description, t.amount_net,
                    t.vat_rate, int(t.vat_deductible), t.date.isoformat(), t.notes,
                ),
            )
            return cur.lastrowid

    def delete(self, tx_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM transactions WHERE id = ?", (tx_id,))

    def get(self, tx_id: int) -> Optional[Transaction]:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM transactions WHERE id = ?", (tx_id,)
            ).fetchone()
        return self._row_to_tx(row) if row else None

    def all(self, limit: int = 500) -> List[Transaction]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM transactions ORDER BY date DESC, id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [self._row_to_tx(r) for r in rows]

    def filter_by_date(self, start: date, end: date) -> List[Transaction]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM transactions WHERE date BETWEEN ? AND ? "
                "ORDER BY date DESC",
                (start.isoformat(), end.isoformat()),
            ).fetchall()
        return [self._row_to_tx(r) for r in rows]

    # --- helpers ------------------------------------------------------
    @staticmethod
    def _row_to_tx(row: sqlite3.Row) -> Transaction:
        return Transaction(
            id=row["id"],
            type=TransactionType(row["type"]),
            category=row["category"],
            description=row["description"],
            amount_net=row["amount_net"],
            vat_rate=row["vat_rate"],
            vat_deductible=bool(row["vat_deductible"]),
            date=date.fromisoformat(row["date"]),
            notes=row["notes"] or "",
        )