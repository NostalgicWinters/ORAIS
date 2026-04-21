import math
from sqlalchemy.orm import Session
from fastapi import HTTPException
from services.products.models import Product
from services.suppliers.models import Supplier
from services.forecasting.models import ForecastResult
from typing import List
from datetime import datetime


def _get_product(db: Session, product_id: int) -> Product:
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p


def _avg_daily_demand(db: Session, product_sku: str, days: int = 30) -> float:
    """Get average daily demand from forecast results or fallback to 1."""
    forecasts = (
        db.query(ForecastResult)
        .filter(ForecastResult.product_sku == product_sku)
        .order_by(ForecastResult.forecast_date.desc())
        .limit(days)
        .all()
    )
    if forecasts:
        return sum(f.predicted_qty for f in forecasts) / len(forecasts)
    return 1.0   # safe fallback


def get_eoq(db: Session, product_id: int) -> dict:
    """
    Economic Order Quantity = sqrt(2 * D * S / H)
      D = annual demand
      S = ordering cost (assumed ₹500)
      H = holding cost (20% of unit cost)
    """
    p = _get_product(db, product_id)
    daily_demand = _avg_daily_demand(db, p.sku)
    annual_demand = daily_demand * 365
    ordering_cost = 500.0
    holding_cost = p.cost_price * 0.20 if p.cost_price else 1.0

    eoq = math.sqrt((2 * annual_demand * ordering_cost) / holding_cost) if holding_cost else 0
    return {
        "product_id": product_id,
        "sku": p.sku,
        "annual_demand": round(annual_demand, 2),
        "eoq": round(eoq, 2),
        "ordering_cost": ordering_cost,
        "holding_cost_per_unit": round(holding_cost, 2),
    }


def get_safety_stock(db: Session, product_id: int) -> dict:
    """
    Safety Stock = Z * sigma_demand * sqrt(lead_time)
    Z = 1.65 for 95% service level
    """
    p = _get_product(db, product_id)
    lead_time = 7   # default

    if p.supplier_id:
        supplier = db.query(Supplier).filter(Supplier.id == p.supplier_id).first()
        if supplier:
            lead_time = supplier.lead_time_days

    forecasts = (
        db.query(ForecastResult)
        .filter(ForecastResult.product_sku == p.sku)
        .all()
    )

    if forecasts:
        import statistics
        demands = [f.predicted_qty for f in forecasts]
        sigma = statistics.stdev(demands) if len(demands) > 1 else demands[0] * 0.2
    else:
        sigma = 2.0

    Z = 1.65
    safety_stock = Z * sigma * math.sqrt(lead_time)
    reorder_point = (_avg_daily_demand(db, p.sku) * lead_time) + safety_stock

    return {
        "product_id": product_id,
        "sku": p.sku,
        "lead_time_days": lead_time,
        "safety_stock": round(safety_stock, 2),
        "reorder_point": round(reorder_point, 2),
        "current_stock": p.stock_qty,
        "needs_reorder": p.stock_qty <= reorder_point,
    }


def get_reorder_recommendations(db: Session) -> List[dict]:
    """All products that need reordering based on safety stock calculation."""
    products = db.query(Product).all()
    recommendations = []

    for p in products:
        result = get_safety_stock(db, p.id)
        if result["needs_reorder"]:
            eoq_result = get_eoq(db, p.id)
            recommendations.append({
                **result,
                "product_name": p.name,
                "recommended_order_qty": eoq_result["eoq"],
                "supplier_id": p.supplier_id,
            })

    return recommendations


def get_stock_alerts(db: Session) -> List[dict]:
    """Products that are below their manually set reorder_point."""
    products = (
        db.query(Product)
        .filter(Product.stock_qty <= Product.reorder_point)
        .all()
    )
    return [
        {
            "product_id": p.id,
            "name": p.name,
            "sku": p.sku,
            "current_stock": p.stock_qty,
            "reorder_point": p.reorder_point,
            "deficit": p.reorder_point - p.stock_qty,
        }
        for p in products
    ]


def get_inventory_turnover(db: Session) -> List[dict]:
    """Inventory turnover ratio = COGS / avg inventory value."""
    from services.orders.models import OrderItem
    products = db.query(Product).all()
    results = []

    for p in products:
        total_sold = (
            db.query(OrderItem)
            .filter(OrderItem.product_id == p.id)
            .all()
        )
        cogs = sum(i.quantity * p.cost_price for i in total_sold)
        avg_inventory_value = p.stock_qty * p.cost_price if p.cost_price else 1
        turnover = cogs / avg_inventory_value if avg_inventory_value else 0

        results.append({
            "product_id": p.id,
            "name": p.name,
            "sku": p.sku,
            "cogs": round(cogs, 2),
            "avg_inventory_value": round(avg_inventory_value, 2),
            "turnover_ratio": round(turnover, 2),
        })

    return sorted(results, key=lambda x: x["turnover_ratio"], reverse=True)
