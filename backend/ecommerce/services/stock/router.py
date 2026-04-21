from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.dependencies import get_current_user
from services.stock import service

router = APIRouter(prefix="/stock", tags=["Stock Optimization"])


@router.get("/optimization")
def reorder_recommendations(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_reorder_recommendations(db)


@router.get("/optimization/{product_id}")
def product_reorder(
    product_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_safety_stock(db, product_id)


@router.get("/eoq/{product_id}")
def eoq(
    product_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_eoq(db, product_id)


@router.get("/safety-stock/{product_id}")
def safety_stock(
    product_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_safety_stock(db, product_id)


@router.get("/alerts")
def stock_alerts(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_stock_alerts(db)


@router.get("/inventory-turnover")
def inventory_turnover(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_inventory_turnover(db)
