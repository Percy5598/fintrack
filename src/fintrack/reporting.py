from . import calculations


def summary(transactions) -> dict:
    """One-stop summary dict used by the dashboard."""
    profit = calculations.profitability(transactions)
    return {
        **profit,
        "output_vat": calculations.output_vat(transactions),
        "deductible_vat": calculations.deductible_vat(transactions),
        "vat_payable": calculations.vat_payable(transactions),
        "transaction_count": len(transactions),
    }


def by_category(transactions) -> dict:
    """Group totals by category (net + VAT) split by type."""
    out = {"income": {}, "expense": {}}
    for t in transactions:
        bucket = out[t.type.value]
        agg = bucket.setdefault(
            t.category, {"net": 0.0, "vat": 0.0, "gross": 0.0, "count": 0}
        )
        agg["net"] += t.amount_net
        agg["vat"] += t.vat_amount
        agg["gross"] += t.amount_gross
        agg["count"] += 1
    # round for JSON friendliness
    for bucket in out.values():
        for agg in bucket.values():
            for k in ("net", "vat", "gross"):
                agg[k] = round(agg[k], 2)
    return out