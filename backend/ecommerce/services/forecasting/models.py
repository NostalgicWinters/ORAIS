from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from core.database import Base


class SalesRecord(Base):
    """Normalized Kaggle retail dataset row."""
    __tablename__ = "sales_records"

    id          = Column(Integer, primary_key=True, index=True)
    product_sku = Column(String, index=True)
    product_name = Column(String)
    category    = Column(String)
    quantity    = Column(Integer)
    unit_price  = Column(Float)
    revenue     = Column(Float)
    sale_date   = Column(DateTime(timezone=True), index=True)
    region      = Column(String)
    source      = Column(String, default="kaggle")   # kaggle | internal
    imported_at = Column(DateTime(timezone=True), server_default=func.now())


class ForecastResult(Base):
    """Cached forecast outputs per product."""
    __tablename__ = "forecast_results"

    id          = Column(Integer, primary_key=True, index=True)
    product_id  = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_sku = Column(String, index=True)
    forecast_date = Column(DateTime(timezone=True), index=True)
    predicted_qty = Column(Float)
    lower_bound = Column(Float)
    upper_bound = Column(Float)
    model_name  = Column(String, default="prophet")
    created_at  = Column(DateTime(timezone=True), server_default=func.now())


class ModelMetric(Base):
    """Tracks accuracy metrics after each training run."""
    __tablename__ = "model_metrics"

    id          = Column(Integer, primary_key=True, index=True)
    model_name  = Column(String)
    mae         = Column(Float)
    rmse        = Column(Float)
    mape        = Column(Float)
    trained_at  = Column(DateTime(timezone=True), server_default=func.now())
    notes       = Column(Text)
