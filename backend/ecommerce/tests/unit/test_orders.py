import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException

from services.orders.service import get_by_id, cancel
from services.orders.models import Order, OrderStatus


def make_order(**kwargs):
    defaults = dict(id=1, customer_id=1, status=OrderStatus.pending,
                    total_amount=500.0, discount=0.0, shipping_fee=0.0,
                    items=[])
    defaults.update(kwargs)
    o = Order(**{k: v for k, v in defaults.items() if hasattr(Order, k)})
    o.status = defaults["status"]
    o.total_amount = defaults["total_amount"]
    o.items = defaults["items"]
    return o


def test_get_by_id_not_found():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    with pytest.raises(HTTPException) as exc:
        get_by_id(db, 999)
    assert exc.value.status_code == 404


def test_cancel_delivered_raises():
    db = MagicMock()
    order = make_order(status=OrderStatus.delivered)
    db.query.return_value.filter.return_value.first.return_value = order
    with pytest.raises(HTTPException) as exc:
        cancel(db, 1)
    assert exc.value.status_code == 400


def test_cancel_pending_succeeds():
    db = MagicMock()
    order = make_order(status=OrderStatus.pending, items=[])
    db.query.return_value.filter.return_value.first.return_value = order
    cancel(db, 1)
    assert order.status == OrderStatus.cancelled
