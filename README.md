
# LedgerFlow — Invoice Management REST API

LedgerFlow is a backend REST API for managing customer invoices, built with Python, Flask, and SQLite.

The project provides invoice CRUD operations, payment status tracking, filtering, and unpaid balance calculations.

## Tech Stack

- Python
- Flask
- SQLite
- pytest
- REST API

## Features

- Create invoices with input validation
- Retrieve all invoices or filter by customer
- Update invoice payment status
- Delete invoices
- Retrieve unpaid invoices
- Calculate total unpaid invoice amounts
- Identify high-priority invoices (amount >= 3000)
- Handle invalid requests and missing resources
- Run automated API tests using pytest

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Health-check homepage |
| GET | `/invoices` | Retrieve all invoices |
| POST | `/invoices` | Create an invoice |
| GET | `/invoices/unpaid` | Retrieve unpaid invoices |
| GET | `/invoices/unpaid-total` | Calculate total unpaid amount |
| GET | `/invoices/high-priority` | Retrieve invoices with amount >= 3000 |
| GET | `/invoices/<customer_name>` | Find invoices by customer |
| PATCH | `/invoices/<invoice_id>` | Update payment status |
| DELETE | `/invoices/<invoice_id>` | Delete an invoice |

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/LedgerFlow.git
cd LedgerFlow
```

Replace `YOUR_USERNAME` with your GitHub username after the repository is created.

### 2. Install dependencies

```bash
python3 -m pip install -r requirements.txt
```

### 3. Initialize the database

```bash
python3 init_db.py
```

### 4. Start the Flask server

```bash
python3 app_sqlite.py
```

The API will be available at:

`http://127.0.0.1:5000`

This project uses Flask's development server for local development and testing.

## Example API Request

Create a new invoice:

```bash
curl -X POST http://127.0.0.1:5000/invoices \
  -H "Content-Type: application/json" \
  -d '{
    "customer": "Qantas",
    "amount": 2500,
    "status": "unpaid"
  }'
```

Retrieve all invoices:

```bash
curl http://127.0.0.1:5000/invoices
```

Update invoice status:

```bash
curl -X PATCH http://127.0.0.1:5000/invoices/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "paid"}'
```

## Automated Testing

Run all tests:

```bash
python3 -m pytest test_app.py -v
```

The project currently includes six automated tests covering:

- Homepage response
- Invoice creation
- Invoice updates
- Invoice deletion
- Deletion of nonexistent invoices (404)
- Invalid invoice amounts (400)

Tests use isolated temporary SQLite databases through pytest fixtures and Flask's test client.

## Future Improvements

- Add authentication and authorization
- Implement pagination and additional filtering
- Add API documentation and deployment configuration
- Build a frontend dashboard using React

## Project Status

Backend MVP v1.0 — local development version.
