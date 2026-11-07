
from datetime import date
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from fintrack.database import (
    initialize_database,
    add_transaction,
    get_transactions,
    delete_transaction,
)
from fintrack.models import Transaction
from fintrack.reporting import calculate_summary


BASE_DIR = Path(__file__).resolve().parent


def create_app():
    """Create and configure the FinTrack Flask application."""

    app = Flask(
        __name__,
        template_folder=str(BASE_DIR / "templates"),
        static_folder=str(BASE_DIR / "static"),
    )

    app.config["JSON_SORT_KEYS"] = False

    # Initialize the SQLite database when the application starts.
    initialize_database()

    @app.route("/", methods=["GET"])
    def index():
        """Render the main dashboard."""
        return render_template("index.html")

    @app.route("/api/transactions", methods=["GET"])
    def transactions():
        """Return all saved transactions."""
        records = get_transactions()
        return jsonify(records), 200

    @app.route("/api/transactions", methods=["POST"])
    def create_transaction():
        """Validate and save a new transaction."""

        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({"error": "A valid JSON object is required."}), 400

        required_fields = [
            "transaction_date",
            "description",
            "category",
            "transaction_type",
            "gross_amount",
            "vat_rate",
        ]

        missing_fields = [
            field for field in required_fields
            if field not in data or data[field] is None
        ]

        if missing_fields:
            return jsonify({
                "error": "Missing required fields.",
                "fields": missing_fields,
            }), 400

        try:
            transaction_date = date.fromisoformat(
                str(data["transaction_date"])
            )

            description = str(data["description"]).strip()
            category = str(data["category"]).strip()
            transaction_type = str(data["transaction_type"]).lower()

            if not description or len(description) > 200:
                raise ValueError("Description must contain 1–200 characters.")

            if not category or len(category) > 80:
                raise ValueError("Category must contain 1–80 characters.")

            if transaction_type not in ("income", "expense"):
                raise ValueError(
                    "Transaction type must be income or expense."
                )

            gross_amount = Decimal(str(data["gross_amount"]))
            vat_percentage = Decimal(str(data["vat_rate"]))

            if not gross_amount.is_finite() or gross_amount <= 0:
                raise ValueError("Gross amount must be a positive number.")

            if not vat_percentage.is_finite() or not (
                Decimal("0") <= vat_percentage <= Decimal("100")
            ):
                raise ValueError("VAT rate must be between 0 and 100.")

            gross_cents = int(
                (gross_amount * 100).quantize(
                    Decimal("1"),
                    rounding=ROUND_HALF_UP,
                )
            )

            # The model stores VAT as a fraction:
            # 25.5% becomes 0.255.
            vat_rate = vat_percentage / Decimal("100")

            vat_deductible = data.get("vat_deductible", False)

            if not isinstance(vat_deductible, bool):
                raise ValueError("vat_deductible must be true or false.")

            # VAT on income is not input VAT that can be deducted.
            if transaction_type == "income":
                vat_deductible = False

            transaction = Transaction(
                transaction_date=transaction_date,
                description=description,
                category=category,
                transaction_type=transaction_type,
                gross_cents=gross_cents,
                vat_rate=vat_rate,
                vat_deductible=vat_deductible,
            )

            transaction_id = add_transaction(transaction)

            return jsonify({
                "message": "Transaction created successfully.",
                "id": transaction_id,
            }), 201

        except (ValueError, InvalidOperation, TypeError) as error:
            return jsonify({"error": str(error)}), 400

    @app.route(
        "/api/transactions/<int:transaction_id>",
        methods=["DELETE"],
    )
    def remove_transaction(transaction_id):
        """Delete a transaction by its database ID."""

        deleted = delete_transaction(transaction_id)

        if not deleted:
            return jsonify({
                "error": "Transaction not found."
            }), 404

        return jsonify({
            "message": "Transaction deleted successfully."
        }), 200

    @app.route("/api/summary", methods=["GET"])
    def summary():
        """Return calculated financial summary."""

        records = get_transactions()
        result = calculate_summary(records)

        # Convert monetary values from cents into euros for the API.
        monetary_fields = [
            "revenue_cents",
            "expenses_cents",
            "profit_cents",
            "sales_vat_cents",
            "purchase_vat_cents",
            "vat_payable_cents",
        ]

        response = {}

        for field in monetary_fields:
            cents = result.get(field, 0)
            response[field.removesuffix("_cents")] = round(cents / 100, 2)

        return jsonify(response), 200

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found."}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "An internal server error occurred."}), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True,
    )
