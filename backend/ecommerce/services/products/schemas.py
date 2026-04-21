from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]

    class Config:
        from_attributes = True


class ProductCreate(BaseModel):
    name: str
    sku: str
    description: Optional[str] = None
    price: float
    cost_price: float = 0.0
    stock_qty: int = 0
    reorder_point: int = 10
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    cost_price: Optional[float] = None
    stock_qty: Optional[int] = None
    reorder_point: Optional[int] = None
    category_id: Optional[int] = None
    supplier_id: Optional[int] = None


class StockUpdate(BaseModel):
    quantity: int
    reason: Optional[str] = "manual_adjustment"


class ProductResponse(BaseModel):
    id: int
    name: str
    sku: str
    description: Optional[str]
    price: float
    cost_price: float
    stock_qty: int
    reorder_point: int
    category_id: Optional[int]
    supplier_id: Optional[int]
    created_at: datetime

    class Config:
        from_attributes = True
