import stripe
import json
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from services.payments.models import Payment
from services.payments.schemas import PaymentCreate, RefundRequest, RevenueReport
from services.orders.models import Order, OrderStatus
from core.config import settings
from typing import List, Optional
from datetime import datetime, timedelta

stripe.api_key = settings.STRIPE_SECRET_KEY


def get_all(db: Session, skip: int = 0, limit: int = 20) -> List[Payment]:
    return db.query(Payment).order_by(Payment.created_at.desc()).offset(skip).limit(limit).all()


def get_by_id(db: Session, payment_id: int) -> Payment:
    p = db.query(Payment).filter(Payment.id == payment_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Payment not found")
    return p


def process_payment(db: Session, data: PaymentCreate) -> Payment:
    order = db.query(Order).filter(Order.id == data.order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status == OrderStatus.cancelled:
        raise HTTPException(status_code=400, detail="Cannot pay for a cancelled order")

    gateway_payment_id = None
    gateway_response = "{}"

    # Real Stripe integration (only runs if key is configured)
    if data.gateway == "stripe" and settings.STRIPE_SECRET_KEY.startswith("sk_"):
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(data.amount * 100),   # paise
                currency=data.currency.lower(),
                payment_method_types=["card"],
                metadata={"order_id": str(data.order_id)},
            )
            gateway_payment_id = intent.id
            gateway_response = json.dumps({"client_secret": intent.client_secret})
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=402, detail=str(e))

    payment = Payment(
        order_id=data.order_id,
        amount=data.amount,
        currency=data.currency,
        method=data.method,
        gateway=data.gateway,
        status="captured" if data.method == "cod" else "pending",
        gateway_payment_id=gateway_payment_id,
        gateway_response=gateway_response,
    )
    db.add(payment)

    if data.method == "cod":
        order.status = OrderStatus.confirmed

    db.commit()
    db.refresh(payment)
    return payment


def refund(db: Session, payment_id: int, data: RefundRequest) -> Payment:
    payment = get_by_id(db, payment_id)
    if payment.status != "captured":
        raise HTTPException(status_code=400, detail="Only captured payments can be refunded")

    refund_amount = data.amount or payment.amount

    if payment.gateway == "stripe" and payment.gateway_payment_id:
        try:
            stripe.Refund.create(
                payment_intent=payment.gateway_payment_id,
                amount=int(refund_amount * 100),
            )
        except stripe.error.StripeError as e:
            raise HTTPException(status_code=402, detail=str(e))

    payment.status = "refunded"
    payment.refund_amount = refund_amount

    order = db.query(Order).filter(Order.id == payment.order_id).first()
    if order:
        order.status = OrderStatus.refunded

    db.commit()
    db.refresh(payment)
    return payment


def handle_webhook(db: Session, payload: bytes, sig_header: str) -> dict:
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    if event["type"] == "payment_intent.succeeded":
        pi_id = event["data"]["object"]["id"]
        payment = db.query(Payment).filter(Payment.gateway_payment_id == pi_id).first()
        if payment:
            payment.status = "captured"
            order = db.query(Order).filter(Order.id == payment.order_id).first()
            if order:
                order.status = OrderStatus.confirmed
            db.commit()

    return {"received": True}


def revenue_report(db: Session, days: int = 30) -> RevenueReport:
    since = datetime.utcnow() - timedelta(days=days)
    payments = (
        db.query(Payment)
        .filter(Payment.status == "captured", Payment.created_at >= since)
        .all()
    )
    total_revenue = sum(p.amount for p in payments)
    total_refunds = sum(p.refund_amount for p in payments)
    total_orders = len(payments)
    avg = total_revenue / total_orders if total_orders else 0.0

    return RevenueReport(
        period=f"Last {days} days",
        total_revenue=total_revenue,
        total_orders=total_orders,
        avg_order_value=avg,
        total_refunds=total_refunds,
    )
