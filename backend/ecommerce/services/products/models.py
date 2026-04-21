from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base


class Category(Base):
    __tablename__ = "categories"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, unique=True, nullable=False)
    description = Column(Text)
    products   = relationship("Product", back_populates="category_rel")


class Product(Base):
    __tablename__ = "products"

    id            = Column(Integer, primary_key=True, index=True)
    name          = Column(String, nullable=False, index=True)
    sku           = Column(String, unique=True, index=True, nullable=False)
    description   = Column(Text)
    price         = Column(Float, nullable=False)
    cost_price    = Column(Float, default=0.0)
    stock_qty     = Column(Integer, default=0)
    reorder_point = Column(Integer, default=10)
    category_id   = Column(Integer, ForeignKey("categories.id"), nullable=True)
    supplier_id   = Column(Integer, ForeignKey("suppliers.id"), nullable=True)
    created_at    = Column(DateTime(timezone=True), server_default=func.now())
    updated_at    = Column(DateTime(timezone=True), onupdate=func.now())

    category_rel  = relationship("Category", back_populates="products")
    supplier      = relationship("Supplier", back_populates="products")
    order_items   = relationship("OrderItem", back_populates="product")
