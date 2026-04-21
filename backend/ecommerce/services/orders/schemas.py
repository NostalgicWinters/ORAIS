from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from services.orders.models import OrderStatus


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    unit_price: float
    subtotal: float

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate]
    shipping_address: Optional[str] = None
    discount: float = 0.0
    shipping_fee: float = 0.0
    notes: Optional[str] = None


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: int
    customer_id: int
    status: str
    total_amount: float
    discount: float
    shipping_fee: float
    shipping_address: Optional[str]
    notes: Optional[str]
    items: List[OrderItemResponse]
    created_at: datetime

    class Config:
        from_attributes = True
