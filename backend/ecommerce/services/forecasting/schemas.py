from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ImportRequest(BaseModel):
    dataset: str = "retailrocket/ecommerce-dataset"   # Kaggle dataset slug
    date_col: str = "InvoiceDate"
    qty_col: str = "Quantity"
    sku_col: str = "StockCode"
    name_col: str = "Description"
    price_col: str = "UnitPrice"


class ForecastRequest(BaseModel):
    product_sku: str
    horizon_days: int = 30


class ForecastPoint(BaseModel):
    date: datetime
    predicted_qty: float
    lower_bound: float
    upper_bound: float


class ForecastResponse(BaseModel):
    product_sku: str
    horizon_days: int
    model: str
    forecast: List[ForecastPoint]


class TrendResponse(BaseModel):
    period: str
    top_products: List[dict]
    revenue_by_week: List[dict]
    seasonal_index: List[dict]


class AccuracyResponse(BaseModel):
    model_name: str
    mae: float
    rmse: float
    mape: float
    trained_at: datetime


class RetrainResponse(BaseModel):
    status: str
    models_trained: int
    metrics: List[AccuracyResponse]
