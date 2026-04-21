"""
Integration tests using FastAPI TestClient with an in-memory SQLite database.
Run with:  pytest tests/integration/test_api.py -v
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from core.database import Base, get_db

# Use in-memory SQLite for tests
SQLITE_URL = "sqlite:///./test.db"
engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def override_get_db():
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


# ── Auth ──────────────────────────────────────────────────────────────────────

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_register_and_login():
    r = client.post("/api/v1/auth/register", json={
        "email": "admin@test.com",
        "full_name": "Admin User",
        "password": "secret123",
        "role": "admin",
    })
    assert r.status_code == 201

    r = client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "secret123",
    })
    assert r.status_code == 200
    data = r.json()
    assert "access_token" in data
    return data["access_token"]


def get_token():
    r = client.post("/api/v1/auth/login", json={
        "email": "admin@test.com",
        "password": "secret123",
    })
    return r.json().get("access_token", "")


# ── Products ──────────────────────────────────────────────────────────────────

def test_create_and_list_products():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post("/api/v1/products/", json={
        "name": "Widget A",
        "sku": "WGT-001",
        "price": 299.99,
        "cost_price": 150.0,
        "stock_qty": 100,
        "reorder_point": 10,
    }, headers=headers)
    assert r.status_code == 201
    assert r.json()["sku"] == "WGT-001"

    r = client.get("/api/v1/products/")
    assert r.status_code == 200
    assert len(r.json()) >= 1


# ── Customers ─────────────────────────────────────────────────────────────────

def test_create_customer():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    r = client.post("/api/v1/customers/", json={
        "full_name": "Jane Doe",
        "email": "jane@example.com",
        "phone": "9876543210",
        "city": "Delhi",
        "country": "IN",
    }, headers=headers)
    assert r.status_code == 201
    assert r.json()["email"] == "jane@example.com"


# ── Orders ────────────────────────────────────────────────────────────────────

def test_create_order():
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"}

    # Get product id
    products = client.get("/api/v1/products/").json()
    product_id = products[0]["id"]

    # Get customer id
    customers = client.get("/api/v1/customers/", headers=headers).json()
    customer_id = customers[0]["id"]

    r = client.post("/api/v1/orders/", json={
        "customer_id": customer_id,
        "items": [{"product_id": product_id, "quantity": 2}],
        "shipping_address": "123 Main St, Delhi",
    }, headers=headers)
    assert r.status_code == 201
    order = r.json()
    assert order["status"] == "pending"
    assert order["total_amount"] > 0
