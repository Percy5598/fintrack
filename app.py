from datetime import date, datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request

from fintrack import calculations, reporting
from fintrack.database import Database
from fintrack.models import Transaction, TransactionType

BASE_DIR = Path(__file__).resolve().parent

app = Flask(
    __name__,
    template_folder=str(BASE_DIR / "templates"),
    static_folder=str(BASE_DIR / "static"),
)
db = Database(BASE_DIR / "data" / "fintrack.db")


# ---------- pages ------------------------------------------------------
@app.get("/")
def index():
    return render_template("index.html")


# ---------- API --------------------------------------------------------
@app.get("/api/transactions")
def list_transactions():
    txs = db.all()
    return jsonify([t.to_dict() for t in txs])


@app.post("/api/transactions")
def create_transaction():
    data = request.get_json(force=True)
    try:
        tx = Transaction(
            id=None,
            type=TransactionType(data["type"]),
            category=data["category"].strip(),
            description=data.get("description", "").strip(),
            amount_net=float(data["amount_net"]),
            vat_rate=float(data.get("vat_rate", 0.0)),
            vat_deductible=bool(data.get("vat_deductible", False)),
            date=datetime.strptime(data["date"], "%Y-%m-%d").date()
            if data.get("date") else date.today(),
            notes=data.get("notes", ""),
        )
    except (KeyError, ValueError) as e:
        return jsonify({"error": f"Invalid payload: {e}"}), 400

    tx.id = db.add(tx)
    return jsonify(tx.to_dict()), 201


@app.delete("/api/transactions/<int:tx_id>")
def delete_transaction(tx_id: int):
    db.delete(tx_id)
    return "", 204


@app.get("/api/report")
def report():
    start = request.args.get("start")
    end = request.args.get("end")
    if start and end:
        txs = db.filter_by_date(
            datetime.strptime(start, "%Y-%m-%d").date(),
            datetime.strptime(end, "%Y-%m-%d").date(),
        )
    else:
        txs = db.all()
    return jsonify({
        "summary": reporting.summary(txs),
        "by_category": reporting.by_category(txs),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)