# LedgerFlow — Invoice API and AI-Assisted AR Analytics

A local portfolio backend built with Python, Flask, SQLite, pandas, and the OpenAI API.

LedgerFlow combines invoice CRUD, accounts receivable reporting, and LLM-backed payment discrepancy analysis.

## Features

- Invoice CRUD with input validation and payment status tracking.
- Unpaid balances, customer filtering, and high-value invoice filtering.
- LLM-backed payment discrepancy analysis with structured responses.
- Exact payment discrepancy arithmetic using Decimal.
- Possible causes explicitly marked as unverified, with verification steps.
- Aging reports with an explicit report date.
- Customer collection priorities based on aggregated overdue balances.
- Single-customer statement of account (SOA) demo.
- Standalone SQLite CTE examples for aging and customer summaries.

## Setup

From the project directory:

```zsh
python3 -m pip install -r requirements.txt
python3 init_db.py
```

For AI analysis, configure an OpenAI API key in the same terminal that will run Flask.
Run the following command first, then paste the key at the hidden prompt:

```zsh
read -s "OPENAI_API_KEY?OpenAI API key: "
```

After entering the key:

```zsh
export OPENAI_API_KEY
printf '\n'
python3 app_sqlite.py
```

The development server runs at http://127.0.0.1:5000.

The default model is `gpt-4o-mini`; override it with `OPENAI_MODEL` if needed.
Real model requests require available API credits and incur usage charges.
Other endpoints do not require an API key.

Keys are read from environment variables. The application does not automatically load `.env`.
Never commit credentials. `.env` and generated `outputs/` reports are ignored.

## API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Homepage |
| GET | `/invoices` | List invoices |
| POST | `/invoices` | Create an invoice |
| GET | `/invoices/unpaid` | List unpaid invoices |
| GET | `/invoices/unpaid-total` | Sum unpaid balances |
| GET | `/invoices/high-priority` | List invoices with amount >= 3000 |
| GET | `/invoices/<customer_name>` | Find invoices by customer |
| PATCH | `/invoices/<invoice_id>` | Update payment status |
| DELETE | `/invoices/<invoice_id>` | Delete an invoice |
| POST | `/payments/analyze` | Analyze a payment discrepancy using an LLM |
| GET | `/reports/aging?report_date=2026-09-16` | Aging summary |
| GET | `/reports/customer-priority?report_date=2026-09-16` | Customer collection priorities |
| GET | `/reports/soa` | Single-customer demo SOA |

Both dated reports require a valid `YYYY-MM-DD` report date.

## Payment Discrepancy Example

```zsh
curl -X POST http://127.0.0.1:5000/payments/analyze \
  -H "Content-Type: application/json" \
  -d '{"invoice_amount":5000,"received_amount":4992,"customer_claim":"Customer claims full payment"}'
```

The application calculates a shortfall of `8`.
The LLM supplies possible explanations and evidence needed to investigate them.
A bank fee is a possible explanation, not an established fact.
The overall analysis and each possible cause are marked `unverified`.
The endpoint does not update invoice status or write off balances.
Model-generated explanations can vary between requests.

Error responses: 400 for invalid input, 502 for provider request failures,
and 503 for missing configuration or an unusable model response.
Provider billing failures currently use the generic 502 response.

## Reporting Rules and Data Sources

- Invoice CRUD uses the local `invoices.db` SQLite database.
- Aging and customer priority APIs use the synthetic `data/invoices.csv`.
  They do not read invoices created through the CRUD API.
- Overdue means unpaid with a due date earlier than the report date.
  Invoices due on the report date are not yet overdue.
- Aging buckets: 0–30, 31–60, 61–90, and over 90 days.
- Customer priorities use total overdue amounts: High >= 5000,
  Medium >= 3000, otherwise Low.
- SOA uses the four `data/soa_*.csv` files for the fixed demo customer `Customer A`.
  These fixtures are separate from the aging dataset.
- SOA payment request = undisputed invoices - unused credits - unallocated payments.
  Disputed invoices remain visible and are excluded from the payment request.
  Allocation still requires confirmation; the report does not post accounting entries.
- SOA currently parses whole-number amounts. Reporting currency, decimal handling,
  excess-credit behavior, and production data validation need further work.

## CSV and Text Exports

```zsh
python3 python/aging_report.py
python3 python/overdue_customer_priority.py
python3 python/soa_generator.py
```

The aging export defaults to the demo report date `2026-09-16`.
Run it before the customer priority export, which reads `outputs/overdue_report.csv`.
Exports are written to `outputs/`. Report API requests do not generate export files.

## SQL Examples

`sql/cte_aging_bucket_summary.sql` and `sql/cte_customer_summary.sql`
contain synthetic fixtures and CTE queries with a fixed report date of `2026-09-16`.

Each script drops and recreates an `invoices` table.
Run them only in an in-memory or disposable SQLite database, never against `invoices.db`.
They are standalone examples and are not executed by the Flask endpoints.

## Tests and Verification

```zsh
python3 -m pytest -q
```

The current suite has 53 tests covering invoice CRUD, payment analysis,
input validation, aging, customer priorities, and SOA calculations.

Automated LLM tests use mocks and do not make paid API calls.
A separate real-provider smoke check returned HTTP 200 for the 5000/4992
payment example, with all possible causes marked unverified.
SQL demo results were also checked in isolated in-memory databases.

## Project Status

Local portfolio MVP. No authentication or production deployment configuration.
Flask runs in development mode. CSV reporting and SQLite CRUD remain separate.
