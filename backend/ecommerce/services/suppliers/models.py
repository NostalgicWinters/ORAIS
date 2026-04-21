from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False, index=True)
    contact_name  = Column(String)
    email         = Column(String, unique=True, index=True)
    phone         = Column(String)
    address       = Column(Text)
    country       = Column(String, default="IN")
    lead_time_days = Column(Integer, default=7)   # avg delivery days
    rating        = Column(Float, default=5.0)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())

    products      = relationship("Product", back_populates="supplier")
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id           = Column(Integer, primary_key=True, index=True)
    supplier_id  = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    status       = Column(String, default="draft")   # draft | ordered | shipped | received | cancelled
    total_cost   = Column(Float, default=0.0)
    notes        = Column(Text)
    expected_at  = Column(DateTime(timezone=True))
    received_at  = Column(DateTime(timezone=True))
    created_at   = Column(DateTime(timezone=True), server_default=func.now())

    supplier     = relationship("Supplier", back_populates="purchase_orders")
    items        = relationship("PurchaseOrderItem", back_populates="purchase_order", cascade="all, delete-orphan")


class PurchaseOrderItem(Base):
    __tablename__ = "purchase_order_items"

    id                = Column(Integer, primary_key=True, index=True)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=False)
    product_id        = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity          = Column(Integer, nullable=False)
    unit_cost         = Column(Float, nullable=False)
    subtotal          = Column(Float, nullable=False)

    purchase_order    = relationship("PurchaseOrder", back_populates="items")
