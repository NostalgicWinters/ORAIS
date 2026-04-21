from sqlalchemy.orm import Session
from fastapi import HTTPException
from services.customers.models import Customer
from services.customers.schemas import CustomerCreate, CustomerUpdate, CustomerLTV
from typing import List, Optional


def get_all(db: Session, skip: int = 0, limit: int = 20, search: Optional[str] = None) -> List[Customer]:
    q = db.query(Customer)
    if search:
        q = q.filter(Customer.full_name.ilike(f"%{search}%") | Customer.email.ilike(f"%{search}%"))
    return q.offset(skip).limit(limit).all()


def get_by_id(db: Session, customer_id: int) -> Customer:
    c = db.query(Customer).filter(Customer.id == customer_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")
    return c


def create(db: Session, data: CustomerCreate) -> Customer:
    if db.query(Customer).filter(Customer.email == data.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    c = Customer(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def update(db: Session, customer_id: int, data: CustomerUpdate) -> Customer:
    c = get_by_id(db, customer_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    db.commit()
    db.refresh(c)
    return c


def delete(db: Session, customer_id: int) -> dict:
    c = get_by_id(db, customer_id)
    db.delete(c)
    db.commit()
    return {"message": f"Customer {customer_id} deleted"}


def get_lifetime_value(db: Session, customer_id: int) -> CustomerLTV:
    c = get_by_id(db, customer_id)
    avg = c.total_spent / c.order_count if c.order_count else 0.0
    if c.total_spent >= 50000:
        segment = "high_value"
    elif c.total_spent >= 10000:
        segment = "mid_value"
    else:
        segment = "low_value"
    return CustomerLTV(
        customer_id=c.id,
        full_name=c.full_name,
        total_spent=c.total_spent,
        order_count=c.order_count,
        avg_order_value=avg,
        segment=segment,
    )


def get_segments(db: Session) -> dict:
    customers = db.query(Customer).all()
    segments = {"high_value": 0, "mid_value": 0, "low_value": 0}
    for c in customers:
        if c.total_spent >= 50000:
            segments["high_value"] += 1
        elif c.total_spent >= 10000:
            segments["mid_value"] += 1
        else:
            segments["low_value"] += 1
    return segments
