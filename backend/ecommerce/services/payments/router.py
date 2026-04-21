from fastapi import APIRouter, Depends, Request, Header, Query
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.dependencies import get_current_user, require_admin
from services.payments import service
from services.payments.schemas import PaymentCreate, RefundRequest, PaymentResponse, RevenueReport

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.get("/", response_model=List[PaymentResponse])
def list_payments(
    skip: int = 0,
    limit: int = Query(20, le=100),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_all(db, skip, limit)


@router.post("/", response_model=PaymentResponse, status_code=201)
def process_payment(
    data: PaymentCreate,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.process_payment(db, data)


@router.get("/report", response_model=RevenueReport)
def revenue_report(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.revenue_report(db, days)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_by_id(db, payment_id)


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(
    payment_id: int,
    data: RefundRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    return service.refund(db, payment_id, data)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None),
    db: Session = Depends(get_db),
):
    payload = await request.body()
    return service.handle_webhook(db, payload, stripe_signature)
