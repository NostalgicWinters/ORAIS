from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.dependencies import get_current_user, require_admin
from services.customers import service
from services.customers.schemas import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerLTV

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.get("/", response_model=List[CustomerResponse])
def list_customers(
    skip: int = 0,
    limit: int = Query(20, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_all(db, skip, limit, search)


@router.post("/", response_model=CustomerResponse, status_code=201)
def create_customer(
    data: CustomerCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.create(db, data)


@router.get("/segments")
def customer_segments(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_segments(db)


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_by_id(db, customer_id)


@router.put("/{customer_id}", response_model=CustomerResponse)
def update_customer(
    customer_id: int,
    data: CustomerUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.update(db, customer_id, data)


@router.delete("/{customer_id}")
def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    return service.delete(db, customer_id)


@router.get("/{customer_id}/lifetime-value", response_model=CustomerLTV)
def lifetime_value(
    customer_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_lifetime_value(db, customer_id)


@router.get("/{customer_id}/orders")
def customer_orders(
    customer_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    from services.orders.service import get_by_customer
    return get_by_customer(db, customer_id)
