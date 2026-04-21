from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from core.database import get_db
from core.dependencies import get_current_user
from services.analytics import service

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard")
def dashboard(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.dashboard_kpis(db, days)


@router.get("/sales")
def sales_over_time(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.sales_by_period(db, days)


@router.get("/top-products")
def top_products(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.top_products(db, limit)


@router.get("/customer-retention")
def customer_retention(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.customer_retention(db)
