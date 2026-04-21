from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id           = Column(Integer, primary_key=True, index=True)
    full_name    = Column(String, nullable=False)
    email        = Column(String, unique=True, index=True, nullable=False)
    phone        = Column(String)
    address      = Column(Text)
    city         = Column(String)
    country      = Column(String, default="IN")
    total_spent  = Column(Float, default=0.0)
    order_count  = Column(Integer, default=0)
    created_at   = Column(DateTime(timezone=True), server_default=func.now())
    updated_at   = Column(DateTime(timezone=True), onupdate=func.now())

    orders       = relationship("Order", back_populates="customer")
