from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from core.database import get_db
from core.dependencies import get_current_user, require_admin
from services.forecasting import service
from services.forecasting.schemas import (
    ImportRequest, ForecastRequest, ForecastResponse,
    TrendResponse, AccuracyResponse, RetrainResponse,
)

router = APIRouter(prefix="/forecasting", tags=["Forecasting"])


@router.post("/import")
def import_dataset(
    data: ImportRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    return service.import_kaggle_dataset(db, data)


@router.post("/predict", response_model=ForecastResponse)
def predict_single(
    data: ForecastRequest,
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.predict_product(db, data)


@router.get("/predict/bulk", response_model=List[ForecastResponse])
def predict_bulk(
    horizon_days: int = Query(30, ge=7, le=365),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.predict_bulk(db, horizon_days)


@router.get("/trends", response_model=TrendResponse)
def get_trends(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_trends(db)


@router.get("/accuracy", response_model=List[AccuracyResponse])
def model_accuracy(
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_user),
):
    return service.get_accuracy(db)


@router.post("/retrain", response_model=RetrainResponse)
def retrain_model(
    db: Session = Depends(get_db),
    _: dict = Depends(require_admin),
):
    return service.retrain(db)
