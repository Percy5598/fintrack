
from datetime import date
from decimal import Decimal

import fintrack.database as database
from fintrack.models import Transaction


def test_database_initialization(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "test.db",
    )

    database.initialize_database()

    assert database.DATABASE_PATH.exists()


def test_add_and_retrieve_transaction(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "test.db",
    )

    database.initialize_database()

    transaction = Transaction(
        transaction_date=date(2026, 11, 7),
        description="Web development",
        category="Services",
        transaction_type="income",
        gross_cents=125500,
        vat_rate=Decimal("0.255"),
    )

    transaction_id = database.add_transaction(transaction)

    records = database.get_transactions()

    assert len(records) == 1
    assert records[0]["id"] == transaction_id
    assert records[0]["description"] == "Web development"
    assert records[0]["gross_cents"] == 125500


def test_get_transaction_by_id(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "test.db",
    )

    database.initialize_database()

    transaction = Transaction(
        transaction_date=date(2026, 11, 7),
        description="Software subscription",
        category="Software",
        transaction_type="expense",
        gross_cents=12550,
        vat_rate=Decimal("0.255"),
        vat_deductible=True,
    )

    transaction_id = database.add_transaction(transaction)

    record = database.get_transaction_by_id(transaction_id)

    assert record is not None
    assert record["category"] == "Software"
    assert record["vat_deductible"] == 1


def test_delete_transaction(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "test.db",
    )

    database.initialize_database()

    transaction = Transaction(
        transaction_date=date(2026, 11, 7),
        description="Client payment",
        category="Services",
        transaction_type="income",
        gross_cents=100000,
        vat_rate=Decimal("0.255"),
    )

    transaction_id = database.add_transaction(transaction)

    assert database.delete_transaction(transaction_id) is True
    assert database.delete_transaction(transaction_id) is False
    assert database.get_transactions() == []


def test_transaction_count(tmp_path, monkeypatch):
    monkeypatch.setattr(
        database,
        "DATABASE_PATH",
        tmp_path / "test.db",
    )

    database.initialize_database()

    assert database.get_transaction_count() == 0

    transaction = Transaction(
        transaction_date=date(2026, 11, 7),
        description="Client payment",
        category="Services",
        transaction_type="income",
        gross_cents=100000,
        vat_rate=Decimal("0.255"),
    )

    database.add_transaction(transaction)

    assert database.get_transaction_count() == 1
