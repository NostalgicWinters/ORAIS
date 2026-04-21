from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id                  = Column(Integer, primary_key=True, index=True)
    order_id            = Column(Integer, ForeignKey("orders.id"), nullable=False)
    amount              = Column(Float, nullable=False)
    currency            = Column(String, default="INR")
    status              = Column(String, default="pending")   # pending | captured | failed | refunded
    method              = Column(String)                       # card | upi | netbanking | cod
    gateway             = Column(String, default="stripe")
    gateway_payment_id  = Column(String, unique=True, index=True)
    gateway_response    = Column(Text)
    refund_id           = Column(String)
    refund_amount       = Column(Float, default=0.0)
    created_at          = Column(DateTime(timezone=True), server_default=func.now())
    updated_at          = Column(DateTime(timezone=True), onupdate=func.now())

    order               = relationship("Order", back_populates="payments")
