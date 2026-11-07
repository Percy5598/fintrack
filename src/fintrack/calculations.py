
from decimal import Decimal, ROUND_HALF_UP


def calculate_vat(gross_cents: int, vat_rate: Decimal) -> int:
    """
    Calculate VAT included in a gross amount.

    Example:
        Gross amount: 125500 cents (€1,255)
        VAT rate: 0.255 (25.5%)
        Result: 25500 cents (€255)
    """

    gross = Decimal(gross_cents)
    rate = Decimal(str(vat_rate))

    if gross < 0:
        raise ValueError("Gross amount cannot be negative.")

    if not rate.is_finite() or not Decimal("0") <= rate <= Decimal("1"):
        raise ValueError("VAT rate must be between 0 and 1.")

    net = gross / (Decimal("1") + rate)

    return int(
        (gross - net).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP,
        )
    )


def calculate_net(gross_cents: int, vat_cents: int) -> int:
    """Calculate net amount by subtracting VAT from gross amount."""

    if not isinstance(gross_cents, int) or not isinstance(vat_cents, int):
        raise TypeError("Amounts must be integer cents.")

    if gross_cents < 0 or vat_cents < 0 or vat_cents > gross_cents:
        raise ValueError("Invalid gross or VAT amount.")

    return gross_cents - vat_cents


def _get_transaction_amounts(transaction):
    """
    Extract financial amounts from either:
    - A Transaction model instance
    - A dictionary returned by the database module
    """

    if isinstance(transaction, dict):
        transaction_type = transaction["transaction_type"]
        gross_cents = int(transaction["gross_cents"])
        vat_rate = Decimal(str(transaction["vat_rate"]))
        vat_deductible = bool(transaction["vat_deductible"])

        vat_cents = calculate_vat(gross_cents, vat_rate)
        net_cents = calculate_net(gross_cents, vat_cents)

        if transaction_type == "expense" and vat_deductible:
            deductible_vat_cents = vat_cents
        else:
            deductible_vat_cents = 0

    else:
        transaction_type = transaction.transaction_type
        gross_cents = transaction.gross_cents
        net_cents = transaction.net_cents
        vat_cents = transaction.vat_cents
        deductible_vat_cents = transaction.deductible_vat_cents

    if transaction_type not in ("income", "expense"):
        raise ValueError("Unknown transaction type.")

    return {
        "transaction_type": transaction_type,
        "gross_cents": gross_cents,
        "net_cents": net_cents,
        "vat_cents": vat_cents,
        "deductible_vat_cents": deductible_vat_cents,
    }


def calculate_summary(transactions):
    """
    Calculate financial totals from a collection of transactions.

    All monetary results are returned in integer cents.
    """

    revenue_cents = 0
    expenses_cents = 0
    sales_vat_cents = 0
    purchase_vat_cents = 0

    income_count = 0
    expense_count = 0

    for transaction in transactions:
        amounts = _get_transaction_amounts(transaction)

        if amounts["transaction_type"] == "income":
            revenue_cents += amounts["net_cents"]
            sales_vat_cents += amounts["vat_cents"]
            income_count += 1

        else:
            expenses_cents += amounts["net_cents"]
            purchase_vat_cents += amounts["deductible_vat_cents"]
            expense_count += 1

    profit_cents = revenue_cents - expenses_cents

    vat_payable_cents = sales_vat_cents - purchase_vat_cents

    return {
        "revenue_cents": revenue_cents,
        "expenses_cents": expenses_cents,
        "profit_cents": profit_cents,
        "sales_vat_cents": sales_vat_cents,
        "purchase_vat_cents": purchase_vat_cents,
        "vat_payable_cents": vat_payable_cents,
        "income_count": income_count,
        "expense_count": expense_count,
        "transaction_count": income_count + expense_count,
    }
