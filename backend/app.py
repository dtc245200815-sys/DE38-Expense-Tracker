
import os
import time
from decimal import Decimal, InvalidOperation

import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, redirect, render_template, request, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "development-only-key")

# Tin cậy proxy khi triển khai sau Nginx.
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "db"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.environ["POSTGRES_DB"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        connect_timeout=3,
    )

def init_db():
    last_error = None

    for attempt in range(30):
        try:
            with get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        CREATE TABLE IF NOT EXISTS transactions (
                            id SERIAL PRIMARY KEY,
                            description VARCHAR(200) NOT NULL,
                            category VARCHAR(100) NOT NULL,
                            transaction_type VARCHAR(10) NOT NULL
                                CHECK (transaction_type IN ('income', 'expense')),
                            amount NUMERIC(14, 2) NOT NULL CHECK (amount > 0),
                            transaction_date DATE NOT NULL DEFAULT CURRENT_DATE,
                            created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
            return
        except psycopg2.Error as exc:
            last_error = exc
            time.sleep(2)

    raise RuntimeError(f"Cannot initialize database: {last_error}")

@app.get("/health")
def health():
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
        return jsonify(status="ok", database="connected")
    except psycopg2.Error:
        app.logger.exception("Database health check failed")
        return jsonify(status="error", database="unavailable"), 503

@app.get("/")
def index():
    with get_connection() as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT
                    COALESCE(SUM(amount) FILTER (
                        WHERE transaction_type = 'income'
                    ), 0) AS total_income,
                    COALESCE(SUM(amount) FILTER (
                        WHERE transaction_type = 'expense'
                    ), 0) AS total_expense
                FROM transactions
            """)
            totals = cur.fetchone()

            cur.execute("""
                SELECT id, description, category, transaction_type,
                       amount, transaction_date
                FROM transactions
                ORDER BY transaction_date DESC, id DESC
            """)
            transactions = cur.fetchall()

    totals["balance"] = totals["total_income"] - totals["total_expense"]

    return render_template(
        "index.html",
        totals=totals,
        transactions=transactions,
    )

@app.post("/transactions")
def add_transaction():
    description = request.form.get("description", "").strip()
    category = request.form.get("category", "").strip()
    transaction_type = request.form.get("transaction_type", "")
    date = request.form.get("transaction_date", "")

    try:
        amount = Decimal(request.form.get("amount", ""))
    except (InvalidOperation, ValueError):
        return "Số tiền không hợp lệ", 400

    if (
        not description or len(description) > 200
        or not category or len(category) > 100
        or transaction_type not in ("income", "expense")
        or not amount.is_finite() or amount <= 0 or amount > Decimal("999999999999.99")
        or not date
    ):
        return "Dữ liệu giao dịch không hợp lệ", 400

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO transactions
                    (description, category, transaction_type, amount, transaction_date)
                VALUES (%s, %s, %s, %s, %s)
            """, (description, category, transaction_type, amount, date))

    app.logger.info("Transaction created: type=%s category=%s", transaction_type, category)
    return redirect(url_for("index"))

@app.post("/transactions/<int:transaction_id>/delete")
def delete_transaction(transaction_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "DELETE FROM transactions WHERE id = %s",
                (transaction_id,),
            )
            deleted = cur.rowcount

    if deleted:
        app.logger.info("Transaction deleted: id=%s", transaction_id)

    return redirect(url_for("index"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
else:
    # Gunicorn imports this module when the container starts.
    init_db()