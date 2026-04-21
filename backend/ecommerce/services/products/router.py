from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from core.database import get_db
from core.dependencies import get_current_user, require_admin
from services.products import service
from services.products.schemas import (
    ProductCreate, ProductUpdate, ProductResponse,
    CategoryCreate, CategoryResponse, StockUpdate,
)

router = APIRouter(prefix="/products", tags=["Products"])


# ── Categories ──────────────────────────────────────────────────────────────

@router.get("/categories", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return service.get_categories(db)


@router.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(
    data: CategoryCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.create_category(db, data)


# ── Products ─────────────────────────────────────────────────────────────────

@router.get("/", response_model=List[ProductResponse])
def list_products(
    skip: int = 0,
    limit: int = Query(20, le=100),
    category_id: Optional[int] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
):
    return service.get_all(db, skip, limit, category_id, search)


@router.get("/low-stock", response_model=List[ProductResponse])
def low_stock(db: Session = Depends(get_db), _: dict = Depends(get_current_user)):
    return service.get_low_stock(db)


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return service.get_by_id(db, product_id)


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(
    data: ProductCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.create(db, data)


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    data: ProductUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.update(db, product_id, data)


@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    return service.delete(db, product_id)


@router.put("/{product_id}/stock", response_model=ProductResponse)
def update_stock(
    product_id: int,
    data: StockUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.update_stock(db, product_id, data)
