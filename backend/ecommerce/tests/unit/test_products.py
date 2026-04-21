import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException

from services.products.service import get_by_id, create, delete, get_low_stock
from services.products.schemas import ProductCreate, StockUpdate
from services.products.models import Product


def make_product(**kwargs):
    defaults = dict(id=1, name="Test", sku="SKU001", price=100.0,
                    cost_price=60.0, stock_qty=50, reorder_point=10,
                    category_id=None, supplier_id=None)
    defaults.update(kwargs)
    p = Product(**defaults)
    return p


# ── get_by_id ─────────────────────────────────────────────────────────────────

def test_get_by_id_found():
    db = MagicMock()
    product = make_product()
    db.query.return_value.filter.return_value.first.return_value = product
    result = get_by_id(db, 1)
    assert result.id == 1


def test_get_by_id_not_found():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        get_by_id(db, 999)
    assert exc.value.status_code == 404


# ── create ────────────────────────────────────────────────────────────────────

def test_create_duplicate_sku():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = make_product()
    data = ProductCreate(name="X", sku="SKU001", price=100.0)
    with pytest.raises(HTTPException) as exc:
        create(db, data)
    assert exc.value.status_code == 400


def test_create_success():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None

    data = ProductCreate(name="New Product", sku="SKU999", price=200.0)
    # Simulate db.refresh populating the object
    def fake_refresh(obj):
        obj.id = 42
    db.refresh.side_effect = fake_refresh

    result = create(db, data)
    db.add.assert_called_once()
    db.commit.assert_called_once()


# ── low stock ─────────────────────────────────────────────────────────────────

def test_get_low_stock_returns_list():
    db = MagicMock()
    low = make_product(stock_qty=5, reorder_point=10)
    db.query.return_value.filter.return_value.all.return_value = [low]
    result = get_low_stock(db)
    assert len(result) == 1
    assert result[0].stock_qty < result[0].reorder_point
