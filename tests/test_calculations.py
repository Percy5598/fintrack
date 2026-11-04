from datetime import date
from decimal import Decimal

from fintrack.models import Transaction, to_cents
from fintrack.reporting import calculate_summary


def test_gross_amount_is_split_into_net_and_vat():
    transaction = Transaction(
        transaction_date=date(2026, 11, 4),
        description="Freelance work",
        category="Services",
        transaction_type="income",
        gross_cents=to_cents("125.50"),
        vat_rate=Decimal("25.5"),
    )

    assert transaction.net_cents == 10000
    assert transaction.vat_cents == 2550


def test_expense_vat_is_not_deductible_when_flag_is_false():
    transaction = Transaction(
        transaction_date=date(2026, 11, 4),
        description="Private expense",
        category="Other",
        transaction_type="expense",
        gross_cents=to_cents("125.50"),
        vat_rate=Decimal("25.5"),
        vat_deductible=False,
    )

    assert transaction.deductible_vat_cents == 0


def test_financial_summary():
    income = Transaction(
        transaction_date=date(2026, 11, 4),
        description="Freelance work",
        category="Services",
        transaction_type="income",
        gross_cents=to_cents("1255"),
        vat_rate=Decimal("25.5"),
    )

    expense = Transaction(
        transaction_date=date(2026, 11, 4),
        description="Business expense",
        category="Other",
        transaction_type="expense",
        gross_cents=to_cents("125.50"),
        vat_rate=Decimal("25.5"),
    )

    summary = calculate_summary([income, expense])

    assert summary["revenue_cents"] == 100000
    assert summary["expenses_cents"] == 10000
    assert summary["profit_cents"] == 90000
    assert summary["vat_payable_cents"] == 22950