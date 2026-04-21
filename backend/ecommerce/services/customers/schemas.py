from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class CustomerCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "IN"


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: Optional[str] = None


class CustomerResponse(BaseModel):
    id: int
    full_name: str
    email: str
    phone: Optional[str]
    address: Optional[str]
    city: Optional[str]
    country: str
    total_spent: float
    order_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class CustomerLTV(BaseModel):
    customer_id: int
    full_name: str
    total_spent: float
    order_count: int
    avg_order_value: float
    segment: str   # high_value | mid_value | low_value
