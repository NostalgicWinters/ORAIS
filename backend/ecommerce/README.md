# E-Commerce Management System API

FastAPI backend with modular microservice-style architecture, Kaggle dataset integration, and ML-powered sales forecasting.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL + SQLAlchemy ORM |
| Migrations | Alembic |
| Auth | JWT (python-jose) + bcrypt |
| ML Forecasting | Prophet (Facebook) + scikit-learn |
| Payments | Stripe |
| Cache/Queue | Redis + Celery |
| Containerization | Docker + Docker Compose |

---

## Project Structure

```
ecommerce/
├── main.py                        # App entry point — registers all routers
├── core/
│   ├── config.py                  # Settings from .env
│   ├── database.py                # SQLAlchemy engine + session
│   ├── dependencies.py            # JWT auth dependencies
│   └── security.py                # Password hashing + token creation
├── services/
│   ├── auth/                      # Register, login, JWT refresh
│   ├── products/                  # Products + categories + stock
│   ├── customers/                 # Customer profiles + LTV + segments
│   ├── orders/                    # Order lifecycle + stock deduction
│   ├── payments/                  # Stripe integration + webhooks
│   ├── suppliers/                 # Supplier management + purchase orders
│   ├── forecasting/               # Kaggle import + Prophet ML forecasting
│   ├── stock/                     # EOQ + safety stock + reorder alerts
│   └── analytics/                 # Dashboard KPIs + sales trends
├── alembic/                       # DB migration scripts
├── tests/
│   ├── unit/                      # Mocked service-level tests
│   └── integration/               # TestClient API tests (SQLite)
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

## Quick Start

### 1. Clone & configure

```bash
cp .env.example .env
# Edit .env with your DATABASE_URL, SECRET_KEY, STRIPE keys, KAGGLE credentials
```

### 2. Run with Docker (recommended)

```bash
docker-compose up --build
```

### 3. Run locally

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start server
uvicorn main:app --reload
```

API will be available at: **http://localhost:8000**
Interactive docs: **http://localhost:8000/api/docs**

---

## API Overview

| Prefix | Service |
|---|---|
| `/api/v1/auth` | Authentication |
| `/api/v1/products` | Products & Categories |
| `/api/v1/customers` | Customer Management |
| `/api/v1/orders` | Order Lifecycle |
| `/api/v1/payments` | Payments & Refunds |
| `/api/v1/suppliers` | Suppliers & Purchase Orders |
| `/api/v1/forecasting` | ML Forecasting (Kaggle) |
| `/api/v1/stock` | Stock Optimization |
| `/api/v1/analytics` | Dashboard & Reports |

---

## Authentication

All protected endpoints require a Bearer token:

```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@shop.com","full_name":"Admin","password":"secret","role":"admin"}'

# 2. Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@shop.com","password":"secret"}'

# 3. Use token
curl http://localhost:8000/api/v1/products/ \
  -H "Authorization: Bearer <your_token>"
```

---

## Kaggle Forecasting Setup

```bash
# 1. Set Kaggle credentials in .env
KAGGLE_USERNAME=your_username
KAGGLE_KEY=your_api_key

# 2. Import dataset
curl -X POST http://localhost:8000/api/v1/forecasting/import \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"dataset": "carrie1/ecommerce-data"}'

# 3. Forecast demand for a SKU
curl -X POST http://localhost:8000/api/v1/forecasting/predict \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"product_sku": "85123A", "horizon_days": 30}'

# 4. Get reorder recommendations
curl http://localhost:8000/api/v1/stock/optimization \
  -H "Authorization: Bearer <token>"
```

---

## Running Tests

```bash
# Unit tests (no DB required)
pytest tests/unit/ -v

# Integration tests (creates test.db SQLite)
pytest tests/integration/ -v

# All tests
pytest -v
```

---

## Each Service File Explained

Every service directory contains exactly 4 files:

| File | Responsibility |
|---|---|
| `models.py` | SQLAlchemy table definitions |
| `schemas.py` | Pydantic request/response shapes |
| `service.py` | All business logic (no HTTP) |
| `router.py` | HTTP routes — calls service layer only |

This separation means you can unit test `service.py` with a mocked DB, and swap out `router.py` independently.
