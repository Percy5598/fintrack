from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from flask import Flask, jsonify, render_template, request

from fintrack.database import (
    add_transaction,
    delete_transaction,
    get_transactions,
    initialize_database,
)
from fintrack.models import Transaction

app = Flask(__name__)

initialize_database()


def money_to_cents(value):
    amount = Decimal(str(value))
    if not amount.is_finite() or amount < 0:
        raise ValueError("Amount must be a non-negative number.")

    return int(
        (amount * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    )


def calculate_net_and_vat(gross_cents, vat_rate):
    rate = Decimal(str(vat_rate))

    if not rate.is_finite() or rate < 0 or rate > 100:
        raise ValueError("VAT rate must be between 0 and 100.")

    fraction = rate / Decimal("100")

    net = (
        Decimal(gross_cents) / (Decimal("1") + fraction)
    ).quantize(Decimal("1"), rounding=ROUND_HALF_UP)

    net_cents = int(net)

    return net_cents, gross_cents - net_cents


def build_summary(rows):
    revenue = 0
    expenses = 0
    sales_vat = 0
    deductible_purchase_vat = 0

    for row in rows:
        gross = int(row["gross_cents"])
        rate = Decimal(str(row["vat_rate"]))
        net, vat = calculate_net_and_vat(gross, rate)

        if row["transaction_type"] == "income":
            revenue += net
            sales_vat += vat
        elif row["transaction_type"] == "expense":
            expenses += net
            if bool(row["vat_deductible"]):
                deductible_purchase_vat += vat

    return {
        "revenue_cents": revenue,
        "expenses_cents": expenses,
        "profit_cents": revenue - expenses,
        "sales_vat_cents": sales_vat,
        "purchase_vat_cents": deductible_purchase_vat,
        "vat_payable_cents": sales_vat - deductible_purchase_vat,
    }


@app.route("/")
def dashboard():
    return render_template("index.html")


@app.route("/api/transactions", methods=["GET"])
def transactions_list():
    return jsonify(get_transactions())


@app.route("/api/transactions", methods=["POST"])
def transactions_create():
    data = request.get_json(silent=True) or {}

    try:
        transaction_type = data.get("transaction_type")
        if transaction_type not in ("income", "expense"):
            raise ValueError("Choose income or expense.")

        description = str(data.get("description", "")).strip()
        category = str(data.get("category", "")).strip()

        if not description or not category:
            raise ValueError("Description and category are required.")

        transaction_date = date.fromisoformat(data["transaction_date"])
        gross_cents = money_to_cents(data["amount"])
        vat_rate = Decimal(str(data["vat_rate"]))

        if not vat_rate.is_finite() or vat_rate < 0 or vat_rate > 1:
            raise ValueError("Invalid VAT rate.")

        vat_deductible = (
            transaction_type == "expense"
            and bool(data.get("vat_deductible", False))
        )

        transaction = Transaction(
            transaction_date=transaction_date,
            description=description,
            category=category,
            transaction_type=transaction_type,
            gross_cents=gross_cents,
            vat_rate=vat_rate,
            vat_deductible=vat_deductible,
        )

        add_transaction(transaction)

        return jsonify({
            "message": "Transaction saved.",
            "transactions": get_transactions(),
        }), 201

    except (KeyError, ValueError, TypeError, InvalidOperation) as error:
        return jsonify({"error": str(error)}), 400


@app.route("/api/transactions/<int:transaction_id>", methods=["DELETE"])
def transactions_delete(transaction_id):
    try:
        delete_transaction(transaction_id)
        return jsonify({
            "message": "Transaction deleted.",
            "transactions": get_transactions(),
        })
    except (ValueError, TypeError) as error:
        return jsonify({"error": str(error)}), 400


@app.route("/api/reports/summary", methods=["GET"])
def reports_summary():
    rows = get_transactions()
    period = request.args.get("period", "all")

    if period != "all":
        try:
            date.fromisoformat(period + "-01")
        except ValueError:
            return jsonify({"error": "Invalid reporting period."}), 400

        rows = [
            row for row in rows
            if row["transaction_date"].startswith(period)
        ]

    return jsonify(build_summary(rows))


@app.route("/api/dashboard", methods=["GET"])
def dashboard_data():
    rows = get_transactions()
    return jsonify({
        "summary": build_summary(rows),
        "transactions": rows,
    })


if __name__ == "__main__":
    app.run(debug=True)