
from datetime import date
from decimal import Decimal

from fintrack.models import Transaction
from fintrack.calculations import (
    calculate_vat,
    calculate_net,
    calculate_summary,
)


def test_calculate_vat():
    assert calculate_vat(125500, Decimal("0.255")) == 25500


def test_calculate_net():
    assert calculate_net(125500, 25500) == 100000


def test_calculate_financial_summary():
    transactions = [
        Transaction(
            transaction_date=date(2026, 11, 7),
            description="Client payment",
            category="Services",
            transaction_type="income",
            gross_cents=125500,
            vat_rate=Decimal("0.255"),
        ),
        Transaction(
            transaction_date=date(2026, 11, 7),
            description="Software subscription",
            category="Software",
            transaction_type="expense",
            gross_cents=12550,
            vat_rate=Decimal("0.255"),
            vat_deductible=True,
        ),
    ]

    summary = calculate_summary(transactions)

    assert summary["revenue_cents"] == 100000
    assert summary["expenses_cents"] == 10000
    assert summary["profit_cents"] == 90000
    assert summary["sales_vat_cents"] == 25500
    assert summary["purchase_vat_cents"] == 2550
    assert summary["vat_payable_cents"] == 22950
    assert summary["transaction_count"] == 2


def test_summary_accepts_database_records():
    records = [
        {
            "transaction_type": "income",
            "gross_cents": 125500,
            "vat_rate": "0.255",
            "vat_deductible": 0,
        },
        {
            "transaction_type": "expense",
            "gross_cents": 12550,
            "vat_rate": "0.255",
            "vat_deductible": 1,
        },
    ]

    summary = calculate_summary(records)

    assert summary["profit_cents"] == 90000
    assert summary["vat_payable_cents"] == 22950
