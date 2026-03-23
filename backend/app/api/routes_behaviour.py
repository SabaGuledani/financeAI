from fastapi import APIRouter, HTTPException, Query

from app.utils.dataset_store import dataset_store
from app.services.behaviour_service import (
    get_spending_by_merchant,
    get_transactions_per_day,
    get_most_active_day,
)

router = APIRouter()


@router.get("/behaviour/spending-by-merchant")
def spending_by_merchant(dataset_id: str = Query(..., description="ID returned by /upload")):
    df = dataset_store.get(dataset_id)

    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found or expired. Please re-upload the file.")

    result = get_spending_by_merchant(df)
    return result.reset_index().to_dict(orient="records")


@router.get("/behaviour/transactions-per-day")
def transactions_per_day(dataset_id: str = Query(..., description="ID returned by /upload")):
    df = dataset_store.get(dataset_id)

    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found or expired. Please re-upload the file.")

    result = get_transactions_per_day(df)
    return result.reset_index().to_dict(orient="records")


@router.get("/behaviour/most-active-day")
def most_active_day(dataset_id: str = Query(..., description="ID returned by /upload")):
    df = dataset_store.get(dataset_id)

    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found or expired. Please re-upload the file.")

    result = get_most_active_day(df)
    return result.reset_index().to_dict(orient="records")
