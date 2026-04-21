from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.dependencies import get_current_user, require_admin
from services.suppliers import service
from services.suppliers.schemas import (
    SupplierCreate, SupplierUpdate, SupplierResponse,
    PurchaseOrderCreate, POStatusUpdate, PurchaseOrderResponse,
)

router = APIRouter(prefix="/suppliers", tags=["Suppliers"])


@router.get("/", response_model=List[SupplierResponse])
def list_suppliers(
    skip: int = 0,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_all(db, skip, limit)


@router.post("/", response_model=SupplierResponse, status_code=201)
def create_supplier(
    data: SupplierCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.create(db, data)


@router.get("/{supplier_id}", response_model=SupplierResponse)
def get_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_by_id(db, supplier_id)


@router.put("/{supplier_id}", response_model=SupplierResponse)
def update_supplier(
    supplier_id: int,
    data: SupplierUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.update(db, supplier_id, data)


@router.delete("/{supplier_id}")
def delete_supplier(
    supplier_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    return service.delete(db, supplier_id)


@router.get("/{supplier_id}/products")
def supplier_products(
    supplier_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_products(db, supplier_id)


@router.get("/{supplier_id}/purchase-orders", response_model=List[PurchaseOrderResponse])
def list_purchase_orders(
    supplier_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_purchase_orders(db, supplier_id)


@router.post("/{supplier_id}/purchase-orders", response_model=PurchaseOrderResponse, status_code=201)
def create_purchase_order(
    supplier_id: int,
    data: PurchaseOrderCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    data.supplier_id = supplier_id
    return service.create_purchase_order(db, data)


@router.put("/purchase-orders/{po_id}", response_model=PurchaseOrderResponse)
def update_po_status(
    po_id: int,
    data: POStatusUpdate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.update_po_status(db, po_id, data)
