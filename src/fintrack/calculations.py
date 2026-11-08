"""
Pure calculation helpers — no I/O, easy to unit test.
"""


def vat_from_net(net: float, rate: float) -> float:
    """VAT amount from a net figure and rate (e.g. 0.24)."""
    return round(net * rate, 2)


def net_from_gross(gross: float, rate: float) -> float:
    """Reverse VAT: net amount given a gross figure."""
    return round(gross / (1 + rate), 2)


def gross_from_net(net: float, rate: float) -> float:
    return round(net * (1 + rate), 2)


def deductible_vat(transactions) -> float:
    """Sum VAT of expenses that are VAT-deductible."""
    total = 0.0
    for t in transactions:
        if t.type.value == "expense" and t.vat_deductible:
            total += t.vat_amount
    return round(total, 2)


def output_vat(transactions) -> float:
    """VAT collected on income (i.e. owed to the tax authority)."""
    return round(sum(t.vat_amount for t in transactions if t.type.value == "income"), 2)


def vat_payable(transactions) -> float:
    """VAT payable = output VAT − deductible VAT."""
    return round(output_vat(transactions) - deductible_vat(transactions), 2)


def profitability(transactions) -> dict:
    """Returns income, expenses, and profit based on *net* amounts."""
    income = sum(t.amount_net for t in transactions if t.type.value == "income")
    expenses = sum(t.amount_net for t in transactions if t.type.value == "expense")
    profit = income - expenses
    margin = (profit / income * 100) if income else 0.0
    return {
        "income_net": round(income, 2),
        "expenses_net": round(expenses, 2),
        "profit_net": round(profit, 2),
        "margin_pct": round(margin, 2),
    }