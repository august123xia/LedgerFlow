from flask import Flask, jsonify, request
import sqlite3
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "invoices.db"



@app.route('/invoices', methods=["POST"])
def create_invoice():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON object is required"
        }), 400

    customer_name = data.get("customer")

    if customer_name is None:
        return jsonify({
            "error": "Customer is required"
        }), 400
    
    if not isinstance(customer_name, str):
        return jsonify({
            "error": "Customer must be a string"
        }), 400

    if customer_name.strip() == "":
        return jsonify({
            "error": "Customer name cannot be empty"
        }), 400  
 
    invoice_amount = data.get("amount")
    if invoice_amount is None:
        return jsonify({
            "error": "Amount is required"
        }), 400
    if isinstance(invoice_amount, bool):
        return jsonify({
            "error": "Amount cannot be a boolean"
        }), 400

    if not isinstance(invoice_amount, (int, float)):
        return jsonify({
            "error": "Amount must be a number"
        }), 400

    if invoice_amount <= 0:
        return jsonify({
            "error": "Amount must be greater than 0"
        }), 400
    
    payment_status = data.get("status")
    if payment_status is None:
        return jsonify({
            "error": "Status is required"
        }), 400

    if payment_status not in ("paid", "unpaid"):
        return jsonify({"error": "Invalid payment status"}), 400
    print("Validation passed")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO invoices (customer, amount, status)
        VALUES (?, ?, ?)
        """,
        (customer_name, invoice_amount, payment_status)
    )

    conn.commit()

    cursor.close()
    conn.close()

    return jsonify({"message": "Invoice created"}), 201


@app.route("/")
def home():
    return "Hello Flask + SQLite"


@app.route("/invoices")
def get_invoices():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id, customer, amount, status FROM invoices")
    rows = cursor.fetchall()

    conn.close()

    result = []

    for row in rows:
        invoice = {
            "id": row[0],
            "customer": row[1],
            "amount": row[2],
            "status": row[3]
        }
        result.append(invoice)

    return jsonify(result)

@app.route("/invoices/unpaid-total")
def get_unpaid_total():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT SUM(amount)
        FROM invoices
        WHERE status = 'unpaid'
    """)

    row = cursor.fetchone()

    conn.close()

    total = row[0]

    return jsonify({"total_unpaid": total})

@app.route("/invoices/unpaid")
def get_unpaid_invoices():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, customer, amount, status
        FROM invoices
        WHERE status = 'unpaid'
    """)

    rows = cursor.fetchall()

    conn.close()

    result = []

    for row in rows:
        invoice = {
            "id": row[0],
            "customer": row[1],
            "amount": row[2],
            "status": row[3]
        }
        result.append(invoice)

    return jsonify(result)

@app.route("/invoices/<int:invoice_id>", methods=["PATCH"])
def update_invoice(invoice_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "A valid JSON object is required"
        }), 400

    new_status = data.get("status")

    if new_status not in ("paid", "unpaid"):
        return jsonify({
            "error": "Invalid payment status"
        }), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        UPDATE invoices
        SET status = ?
        WHERE id = ?
        """,
        (new_status, invoice_id)
    )

    updated_rows = cursor.rowcount

    conn.commit()
    cursor.close()
    conn.close()

    if updated_rows == 0:
        return jsonify({
            "error": "Invoice not found"
        }), 404

    return jsonify({
        "message": "Invoice updated successfully"
    }), 200


@app.route("/invoices/<int:invoice_id>", methods=["DELETE"])
def delete_invoice(invoice_id):

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM invoices
        WHERE id = ?
        """,
        (invoice_id,)
    )

    deleted_rows = cursor.rowcount

    conn.commit()

    cursor.close()
    conn.close()

    if deleted_rows == 0:
        return jsonify({
            "error": "Invoice not found"
        }), 404

    return jsonify({
        "message": "Invoice deleted successfully"
    }), 200


@app.route("/invoices/high-priority")
def get_high_priority_invoices():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, customer, amount, status
        FROM invoices
        WHERE amount >= 3000
    """)

    rows = cursor.fetchall()

    conn.close()

    result = []

    for row in rows:
        invoice = {
            "id": row[0],
            "customer": row[1],
            "amount": row[2],
            "status": row[3]
        }
        result.append(invoice)

    return jsonify(result)

@app.route("/invoices/<customer_name>")
def get_invoices_by_customer(customer_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, customer, amount, status
        FROM invoices
        WHERE customer = ?
    """, (customer_name,))

    rows = cursor.fetchall()

    conn.close()

    result = []

    for row in rows:
        invoice = {
            "id": row[0],
            "customer": row[1],
            "amount": row[2],
            "status": row[3]
        }
        result.append(invoice)

    if len(result) == 0:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)