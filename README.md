# Business Workflow Automation API

A FastAPI application for managing products, inventory, customer orders, payment confirmation, sales, and audit events. It uses SQLAlchemy for persistence and SQLite by default.

## Requirements

- Python 3.10 or newer
- pip

## Setup

From the project directory, create and activate a virtual environment, then install the dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Start the API:

```powershell
uvicorn app.main:app --reload
```

The default database is `business.db` in the project directory. Set `DATABASE_URL` to use another SQLAlchemy database URL, or set `APP_NAME` to change the API title. For example, in PowerShell:

```powershell
$env:DATABASE_URL = "sqlite:///./business.db"
$env:APP_NAME = "Business Workflow Automation"
```

The application creates missing tables at startup. Schema migrations are not currently configured.

## API

Interactive API documentation is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) after startup.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Check that the API is running |
| `GET` | `/products/` | List products |
| `POST` | `/products/` | Create a product |
| `POST` | `/orders/` | Create an order |
| `POST` | `/payments/{order_id}/confirm` | Confirm an order's payment |
| `POST` | `/inventory/{product_id}/reduce?quantity=...` | Reduce available stock |
| `POST` | `/inventory/{product_id}/restock?quantity=...` | Add stock and resume eligible waiting orders |

### Example requests

Create a product:

```json
{
  "name": "Coffee",
  "stock": 10,
  "price_per_kg": 12.5
}
```

Create an order:

```json
{
  "customer_name": "Alex",
  "product_id": 1,
  "quantity": 2,
  "amount_paid": 25
}
```

Confirm payment:

```json
{
  "amount_paid": 25
}
```

Products require a non-empty name, non-negative stock, and a positive price. Orders require a positive product ID and quantity and a non-negative payment amount. Inventory adjustments require a positive `quantity`.

Orders can be completed immediately when stock and payment are sufficient. Otherwise, they may wait for payment or stock. Restocking resumes fully paid stock-waiting orders in FIFO order.

## Tests

Run the API regression tests with Python's built-in test runner:

```powershell
python -m unittest discover -s tests -v
```
