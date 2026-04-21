from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class PaymentCreate(BaseModel):
    order_id: int
    amount: float
    currency: str = "INR"
    method: str   # card | upi | netbanking | cod
    gateway: str = "stripe"


class RefundRequest(BaseModel):
    amount: Optional[float] = None   # None = full refund
    reason: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    order_id: int
    amount: float
    currency: str
    status: str
    method: str
    gateway: str
    gateway_payment_id: Optional[str]
    refund_amount: float
    created_at: datetime

    class Config:
        from_attributes = True


class RevenueReport(BaseModel):
    period: str
    total_revenue: float
    total_orders: int
    avg_order_value: float
    total_refunds: float
