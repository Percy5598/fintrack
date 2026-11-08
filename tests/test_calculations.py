from datetime import date

import pytest

from fintrack import calculations
from fintrack.models import Transaction, TransactionType


def tx(type_, net, vat, deductible=False):
    return Transaction(
        id=None, type=type_, category="x", description="x",
        amount_net=net, vat_rate=vat, vat_deductible=deductible,
        date=date(2025, 1, 1),
    )


def test_vat_from_net():
    assert calculations.vat_from_net(100, 0.24) == 24.0
    assert calculations.vat_from_net(99.99, 0.24) == 24.0

def test_net_from_gross():
    assert calculations.net_from_gross(124, 0.24) == 100.0

def test_gross_from_net():
    assert calculations.gross_from_net(100, 0.24) == 124.0

def test_output_and_deductible_vat():
    txs = [
        tx(TransactionType.INCOME, 1000, 0.24),
        tx(TransactionType.EXPENSE, 200, 0.24, deductible=True),
        tx(TransactionType.EXPENSE, 100, 0.24, deductible=False),
    ]
    assert calculations.output_vat(txs) == 240.0
    assert calculations.deductible_vat(txs) == 48.0
    assert calculations.vat_payable(txs) == 192.0

def test_profitability():
    txs = [
        tx(TransactionType.INCOME, 1000, 0.0),
        tx(TransactionType.EXPENSE, 400, 0.0),
    ]
    r = calculations.profitability(txs)
    assert r["profit_net"] == 600.0
    assert r["margin_pct"] == 60.0