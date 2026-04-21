from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class SupplierCreate(BaseModel):
    name: str
    contact_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    address: Optional[str] = None
    country: str = "IN"
    lead_time_days: int = 7


class SupplierUpdate(BaseModel):
    name: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    lead_time_days: Optional[int] = None
    rating: Optional[float] = None


class SupplierResponse(BaseModel):
    id: int
    name: str
    contact_name: Optional[str]
    email: str
    phone: Optional[str]
    country: str
    lead_time_days: int
    rating: float
    created_at: datetime

    class Config:
        from_attributes = True


# ── Purchase Orders ───────────────────────────────────────────────────────────

class POItemCreate(BaseModel):
    product_id: int
    quantity: int
    unit_cost: float


class POItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_cost: float
    subtotal: float

    class Config:
        from_attributes = True


class PurchaseOrderCreate(BaseModel):
    supplier_id: int
    items: List[POItemCreate]
    notes: Optional[str] = None
    expected_at: Optional[datetime] = None


class POStatusUpdate(BaseModel):
    status: str   # draft | ordered | shipped | received | cancelled


class PurchaseOrderResponse(BaseModel):
    id: int
    supplier_id: int
    status: str
    total_cost: float
    notes: Optional[str]
    expected_at: Optional[datetime]
    received_at: Optional[datetime]
    items: List[POItemResponse]
    created_at: datetime

    class Config:
        from_attributes = True
