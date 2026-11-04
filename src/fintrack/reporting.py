from decimal import Decimal

from fintrack.models import Transaction


def calculate_summary(
    transactions: list[Transaction],
) -> dict[str, int]:
    """Calculate financial totals in integer cents."""

    income = [
        transaction
        for transaction in transactions
        if transaction.transaction_type == "income"
    ]

    expenses = [
        transaction
        for transaction in transactions
        if transaction.transaction_type == "expense"
    ]

    revenue_cents = sum(
        transaction.net_cents for transaction in income
    )

    expenses_cents = sum(
        transaction.net_cents for transaction in expenses
    )

    sales_vat_cents = sum(
        transaction.vat_cents for transaction in income
    )

    purchase_vat_cents = sum(
        transaction.deductible_vat_cents for transaction in expenses
    )

    return {
        "revenue_cents": revenue_cents,
        "expenses_cents": expenses_cents,
        "profit_cents": revenue_cents - expenses_cents,
        "sales_vat_cents": sales_vat_cents,
        "purchase_vat_cents": purchase_vat_cents,
        "vat_payable_cents": sales_vat_cents - purchase_vat_cents,
    }