from sqlalchemy.orm import Session
from fastapi import HTTPException
from services.orders.models import Order, OrderItem, OrderStatus
from services.orders.schemas import OrderCreate, OrderStatusUpdate
from services.products.models import Product
from services.customers.models import Customer
from typing import List, Optional


def get_all(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
    customer_id: Optional[int] = None,
) -> List[Order]:
    q = db.query(Order)
    if status:
        q = q.filter(Order.status == status)
    if customer_id:
        q = q.filter(Order.customer_id == customer_id)
    return q.order_by(Order.created_at.desc()).offset(skip).limit(limit).all()


def get_by_id(db: Session, order_id: int) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


def get_by_customer(db: Session, customer_id: int) -> List[Order]:
    return db.query(Order).filter(Order.customer_id == customer_id).all()


def create(db: Session, data: OrderCreate) -> Order:
    # Validate customer
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Build order
    order = Order(
        customer_id=data.customer_id,
        shipping_address=data.shipping_address,
        discount=data.discount,
        shipping_fee=data.shipping_fee,
        notes=data.notes,
        status=OrderStatus.pending,
    )
    db.add(order)
    db.flush()  # get order.id without committing

    total = 0.0
    for item_data in data.items:
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item_data.product_id} not found")
        if product.stock_qty < item_data.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product '{product.name}' (available: {product.stock_qty})",
            )

        subtotal = product.price * item_data.quantity
        total += subtotal

        item = OrderItem(
            order_id=order.id,
            product_id=product.id,
            quantity=item_data.quantity,
            unit_price=product.price,
            subtotal=subtotal,
        )
        db.add(item)

        # Deduct stock
        product.stock_qty -= item_data.quantity

    order.total_amount = total - data.discount + data.shipping_fee

    # Update customer stats
    customer.total_spent += order.total_amount
    customer.order_count += 1

    db.commit()
    db.refresh(order)
    return order


def update_status(db: Session, order_id: int, data: OrderStatusUpdate) -> Order:
    order = get_by_id(db, order_id)
    order.status = data.status
    db.commit()
    db.refresh(order)
    return order


def cancel(db: Session, order_id: int) -> Order:
    order = get_by_id(db, order_id)
    if order.status in [OrderStatus.delivered, OrderStatus.cancelled]:
        raise HTTPException(status_code=400, detail=f"Cannot cancel a {order.status} order")

    # Restore stock
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if product:
            product.stock_qty += item.quantity

    # Update customer stats
    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    if customer:
        customer.total_spent -= order.total_amount
        customer.order_count -= 1

    order.status = OrderStatus.cancelled
    db.commit()
    db.refresh(order)
    return order
