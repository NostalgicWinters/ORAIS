from sqlalchemy.orm import Session
from fastapi import HTTPException
from datetime import datetime
from services.suppliers.models import Supplier, PurchaseOrder, PurchaseOrderItem
from services.suppliers.schemas import (
    SupplierCreate, SupplierUpdate,
    PurchaseOrderCreate, POStatusUpdate,
)
from services.products.models import Product
from typing import List


# ── Suppliers ────────────────────────────────────────────────────────────────

def get_all(db: Session, skip: int = 0, limit: int = 20) -> List[Supplier]:
    return db.query(Supplier).offset(skip).limit(limit).all()


def get_by_id(db: Session, supplier_id: int) -> Supplier:
    s = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not s:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return s


def create(db: Session, data: SupplierCreate) -> Supplier:
    if db.query(Supplier).filter(Supplier.email == data.email).first():
        raise HTTPException(status_code=400, detail="Supplier email already exists")
    s = Supplier(**data.model_dump())
    db.add(s)
    db.commit()
    db.refresh(s)
    return s


def update(db: Session, supplier_id: int, data: SupplierUpdate) -> Supplier:
    s = get_by_id(db, supplier_id)
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(s, k, v)
    db.commit()
    db.refresh(s)
    return s


def delete(db: Session, supplier_id: int) -> dict:
    s = get_by_id(db, supplier_id)
    db.delete(s)
    db.commit()
    return {"message": f"Supplier {supplier_id} deleted"}


def get_products(db: Session, supplier_id: int) -> List[Product]:
    get_by_id(db, supplier_id)
    return db.query(Product).filter(Product.supplier_id == supplier_id).all()


# ── Purchase Orders ───────────────────────────────────────────────────────────

def get_purchase_orders(db: Session, supplier_id: int) -> List[PurchaseOrder]:
    get_by_id(db, supplier_id)
    return db.query(PurchaseOrder).filter(PurchaseOrder.supplier_id == supplier_id).all()


def create_purchase_order(db: Session, data: PurchaseOrderCreate) -> PurchaseOrder:
    get_by_id(db, data.supplier_id)

    po = PurchaseOrder(
        supplier_id=data.supplier_id,
        notes=data.notes,
        expected_at=data.expected_at,
        status="draft",
    )
    db.add(po)
    db.flush()

    total = 0.0
    for item_data in data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item_data.product_id} not found")
        subtotal = item_data.quantity * item_data.unit_cost
        total += subtotal
        poi = PurchaseOrderItem(
            purchase_order_id=po.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_cost=item_data.unit_cost,
            subtotal=subtotal,
        )
        db.add(poi)

    po.total_cost = total
    db.commit()
    db.refresh(po)
    return po


def update_po_status(db: Session, po_id: int, data: POStatusUpdate) -> PurchaseOrder:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == po_id).first()
    if not po:
        raise HTTPException(status_code=404, detail="Purchase order not found")

    po.status = data.status

    # When received: add stock to products
    if data.status == "received":
        po.received_at = datetime.utcnow()
        for item in po.items:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                product.stock_qty += item.quantity

    db.commit()
    db.refresh(po)
    return po
