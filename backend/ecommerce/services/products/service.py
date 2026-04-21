from sqlalchemy.orm import Session
from fastapi import HTTPException
from services.products.models import Product, Category
from services.products.schemas import ProductCreate, ProductUpdate, CategoryCreate, StockUpdate
from typing import List, Optional


# ── Categories ──────────────────────────────────────────────────────────────

def get_categories(db: Session) -> List[Category]:
    return db.query(Category).all()


def create_category(db: Session, data: CategoryCreate) -> Category:
    if db.query(Category).filter(Category.name == data.name).first():
        raise HTTPException(status_code=400, detail="Category already exists")
    cat = Category(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


# ── Products ─────────────────────────────────────────────────────────────────

def get_all(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    category_id: Optional[int] = None,
    search: Optional[str] = None,
) -> List[Product]:
    q = db.query(Product)
    if category_id:
        q = q.filter(Product.category_id == category_id)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%"))
    return q.offset(skip).limit(limit).all()


def get_by_id(db: Session, product_id: int) -> Product:
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return p


def create(db: Session, data: ProductCreate) -> Product:
    if db.query(Product).filter(Product.sku == data.sku).first():
        raise HTTPException(status_code=400, detail="SKU already exists")
    p = Product(**data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def update(db: Session, product_id: int, data: ProductUpdate) -> Product:
    p = get_by_id(db, product_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(p, k, v)
    db.commit()
    db.refresh(p)
    return p


def delete(db: Session, product_id: int) -> dict:
    p = get_by_id(db, product_id)
    db.delete(p)
    db.commit()
    return {"message": f"Product {product_id} deleted"}


def update_stock(db: Session, product_id: int, data: StockUpdate) -> Product:
    p = get_by_id(db, product_id)
    p.stock_qty = data.quantity
    db.commit()
    db.refresh(p)
    return p


def get_low_stock(db: Session) -> List[Product]:
    return (
        db.query(Product)
        .filter(Product.stock_qty <= Product.reorder_point)
        .all()
    )
