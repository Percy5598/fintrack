from datetime import date

from fintrack.database import Database
from fintrack.models import Transaction, TransactionType


def make_tx():
    return Transaction(
        id=None, type=TransactionType.INCOME, category="Consulting",
        description="Client A", amount_net=1000.0, vat_rate=0.24,
        vat_deductible=False, date=date(2025, 3, 1),
    )


def test_add_and_fetch(tmp_path):
    db = Database(tmp_path / "t.db")
    tx_id = db.add(make_tx())
    assert tx_id == 1

    got = db.get(tx_id)
    assert got.description == "Client A"
    assert got.amount_net == 1000.0
    assert got.vat_amount == 240.0
    assert got.amount_gross == 1240.0


def test_delete(tmp_path):
    db = Database(tmp_path / "t.db")
    tx_id = db.add(make_tx())
    db.delete(tx_id)
    assert db.get(tx_id) is None


def test_filter_by_date(tmp_path):
    db = Database(tmp_path / "t.db")
    db.add(make_tx())
    in_range = db.filter_by_date(date(2025, 1, 1), date(2025, 12, 31))
    out_range = db.filter_by_date(date(2024, 1, 1), date(2024, 12, 31))
    assert len(in_range) == 1
    assert len(out_range) == 0