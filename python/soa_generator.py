import csv
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "outputs"


def read_csv_file(file_path):
    rows = []

    with open(file_path, "r") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row["amount"] = int(row["amount"])
            rows.append(row)

    return rows


def calculate_total(rows):
    total = 0

    for row in rows:
        total += row["amount"]

    return total


def format_undisputed_lines(invoices):
    lines = ""

    for invoice in invoices:
        lines += f'{invoice["invoice_no"]} | {invoice["due_date"]} | ${invoice["amount"]:,.2f}\n'

    return lines


def format_disputed_lines(invoices):
    lines = ""

    for invoice in invoices:
        lines += f'{invoice["invoice_no"]} | {invoice["due_date"]} | ${invoice["amount"]:,.2f} | {invoice["reason"]}\n'

    return lines


def format_credit_lines(credits):
    lines = ""

    for credit in credits:
        lines += f'{credit["credit_no"]} | ${credit["amount"]:,.2f}\n'

    return lines


def format_payment_lines(payments):
    lines = ""

    for payment in payments:
        lines += f'{payment["payment_ref"]} | {payment["payment_date"]} | ${payment["amount"]:,.2f}\n'

    return lines


def build_soa():
    customer_name = "Customer A"

    undisputed_invoices = read_csv_file(DATA_DIR / "soa_undisputed_invoices.csv")
    disputed_invoices = read_csv_file(DATA_DIR / "soa_disputed_invoices.csv")
    unused_credits = read_csv_file(DATA_DIR / "soa_unused_credits.csv")
    unallocated_payments = read_csv_file(DATA_DIR / "soa_unallocated_payments.csv")

    total_undisputed = calculate_total(undisputed_invoices)
    total_disputed = calculate_total(disputed_invoices)
    total_unused_credits = calculate_total(unused_credits)
    total_unallocated_payments = calculate_total(unallocated_payments)

    payment_request = (
        total_undisputed
        - total_unused_credits
        - total_unallocated_payments
    )

    undisputed_lines = format_undisputed_lines(undisputed_invoices)
    disputed_lines = format_disputed_lines(disputed_invoices)
    credit_lines = format_credit_lines(unused_credits)
    payment_lines = format_payment_lines(unallocated_payments)

    soa_text = f"""Dear {customer_name},

Please find below the current statement of account summary.

1. Undisputed Unpaid Invoices
Invoice No | Due Date | Amount
{undisputed_lines}
Total undisputed unpaid amount: ${total_undisputed:,.2f}

2. Invoices Under Dispute
Invoice No | Due Date | Amount | Reason
{disputed_lines}
Total disputed amount: ${total_disputed:,.2f}

These disputed invoices are shown for visibility but are not included in the immediate payment request.

3. Unused Credits
Credit No | Amount
{credit_lines}
Total unused credits: ${total_unused_credits:,.2f}

4. Unallocated Payments
Payment Ref | Payment Date | Amount
{payment_lines}
Total unallocated payments: ${total_unallocated_payments:,.2f}

Could you please confirm how the unused credits and unallocated payments should be allocated?

After excluding invoices under dispute, unused credits, and unallocated payments, the current amount requested for payment is: ${payment_request:,.2f}.

Please arrange payment for the undisputed overdue amount at your earliest convenience.

Kind regards,
AR Team
"""

    return {
        "customer": customer_name,
        "total_undisputed": total_undisputed,
        "total_disputed": total_disputed,
        "total_unused_credits": total_unused_credits,
        "total_unallocated_payments": total_unallocated_payments,
        "payment_request": payment_request,
        "statement_text": soa_text,
    }


def generate_soa():
    result = build_soa()
    soa_text = result["statement_text"]
    total_undisputed = result["total_undisputed"]
    total_disputed = result["total_disputed"]
    total_unused_credits = result["total_unused_credits"]
    total_unallocated_payments = result["total_unallocated_payments"]
    payment_request = result["payment_request"]

    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / "customer_soa.txt"

    with open(output_path, "w") as file:
        file.write(soa_text)

    print("SOA summary generated successfully.")
    print(f"Output file: {output_path}")
    print(f"Total undisputed: ${total_undisputed:,.2f}")
    print(f"Total disputed: ${total_disputed:,.2f}")
    print(f"Total unused credits: ${total_unused_credits:,.2f}")
    print(f"Total unallocated payments: ${total_unallocated_payments:,.2f}")
    print(f"Payment request: ${payment_request:,.2f}")


if __name__ == "__main__":
    generate_soa()
