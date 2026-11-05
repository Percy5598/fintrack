from decimal import Decimal, ROUND_HALF_UP


def money(value):
    """Round a monetary value to two decimal places."""
    return Decimal(str(value)).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )


def calculate_vat(amount, vat_rate):
    """Calculate VAT on an amount excluding VAT."""
    amount = Decimal(str(amount))
    vat_rate = Decimal(str(vat_rate))

    return money(amount * vat_rate / Decimal("100"))


def calculate_financial_summary(income, expenses):
    """
    Calculate revenue, expenses, VAT, and estimated profit.

    Income and expenses must be lists of dictionaries
    containing amount and vat_rate.
    """
    revenue = sum(
        (money(item["amount"]) for item in income),
        Decimal("0.00")
    )

    total_expenses = sum(
        (money(item["amount"]) for item in expenses),
        Decimal("0.00")
    )

    sales_vat = sum(
        (calculate_vat(item["amount"], item["vat_rate"])
         for item in income),
        Decimal("0.00")
    )

    purchase_vat = sum(
        (calculate_vat(item["amount"], item["vat_rate"])
         for item in expenses),
        Decimal("0.00")
    )

    estimated_profit = money(revenue - total_expenses)
    estimated_vat_payable = money(sales_vat - purchase_vat)

    return {
        "revenue": revenue,
        "expenses": total_expenses,
        "profit": estimated_profit,
        "sales_vat": sales_vat,
        "purchase_vat": purchase_vat,
        "vat_payable": estimated_vat_payable,
    }