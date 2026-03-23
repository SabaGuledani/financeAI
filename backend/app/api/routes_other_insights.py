from fastapi import APIRouter, HTTPException, Query

from app.utils.dataset_store import dataset_store
from app.services.other_insights_service import (
    get_anomaly_transactions,
    get_month_category_comparison,
)

router = APIRouter()


@router.get("/other-insights/anomaly-transactions")
def anomaly_transactions(
    dataset_id: str = Query(..., description="ID returned by /upload"),
    currency: str = Query("GEL", description="Currency column to detect anomalies in (GEL, USD, EUR, GBP)"),
):
    df = dataset_store.get(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found or expired. Please re-upload the file.")
    result = get_anomaly_transactions(df, currency=currency)
    return result.to_dict(orient="records")


@router.get("/other-insights/month-category-comparison")
def month_category_comparison(
    dataset_id: str = Query(..., description="ID returned by /upload"),
    currency: str = Query("GEL", description="Currency column to compare spending by (GEL, USD, EUR, GBP)"),
):
    df = dataset_store.get(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found or expired. Please re-upload the file.")
    message = get_month_category_comparison(df, currency=currency)
    return {"message": message}
