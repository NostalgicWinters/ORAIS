from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from services.orders.models import Order, OrderItem, OrderStatus
from services.payments.models import Payment
from services.customers.models import Customer
from services.products.models import Product
from typing import List


def dashboard_kpis(db: Session, days: int = 30) -> dict:
    since = datetime.utcnow() - timedelta(days=days)

    total_revenue = (
        db.query(func.sum(Payment.amount))
        .filter(Payment.status == "captured", Payment.created_at >= since)
        .scalar() or 0.0
    )
    total_orders = (
        db.query(func.count(Order.id))
        .filter(Order.created_at >= since)
        .scalar() or 0
    )
    new_customers = (
        db.query(func.count(Customer.id))
        .filter(Customer.created_at >= since)
        .scalar() or 0
    )
    total_products = db.query(func.count(Product.id)).scalar() or 0
    low_stock_count = (
        db.query(func.count(Product.id))
        .filter(Product.stock_qty <= Product.reorder_point)
        .scalar() or 0
    )
    pending_orders = (
        db.query(func.count(Order.id))
        .filter(Order.status == OrderStatus.pending)
        .scalar() or 0
    )
    avg_order_value = total_revenue / total_orders if total_orders else 0.0

    return {
        "period_days": days,
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "new_customers": new_customers,
        "avg_order_value": round(avg_order_value, 2),
        "total_products": total_products,
        "low_stock_products": low_stock_count,
        "pending_orders": pending_orders,
    }


def top_products(db: Session, limit: int = 10) -> List[dict]:
    results = (
        db.query(
            Product.id,
            Product.name,
            Product.sku,
            func.sum(OrderItem.quantity).label("units_sold"),
            func.sum(OrderItem.subtotal).label("revenue"),
        )
        .join(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Product.id)
        .order_by(func.sum(OrderItem.subtotal).desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "product_id": r.id,
            "name": r.name,
            "sku": r.sku,
            "units_sold": r.units_sold,
            "revenue": round(r.revenue, 2),
        }
        for r in results
    ]


def sales_by_period(db: Session, days: int = 30) -> List[dict]:
    since = datetime.utcnow() - timedelta(days=days)
    orders = (
        db.query(Order)
        .filter(Order.created_at >= since, Order.status != OrderStatus.cancelled)
        .all()
    )
    daily: dict = {}
    for o in orders:
        day = o.created_at.date().isoformat()
        daily[day] = daily.get(day, 0) + o.total_amount

    return [{"date": k, "revenue": round(v, 2)} for k, v in sorted(daily.items())]


def customer_retention(db: Session) -> dict:
    total = db.query(func.count(Customer.id)).scalar() or 1
    repeat = (
        db.query(func.count(Customer.id))
        .filter(Customer.order_count > 1)
        .scalar() or 0
    )
    return {
        "total_customers": total,
        "repeat_customers": repeat,
        "retention_rate": round((repeat / total) * 100, 2),
        "churn_rate": round(((total - repeat) / total) * 100, 2),
    }
