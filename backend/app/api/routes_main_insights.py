from fastapi import APIRouter, HTTPException, Query

from app.utils.dataset_store import dataset_store
from app.services.main_insights_service import (
    get_spending_by_month,
    get_spending_by_category,
    get_total_spending,
    get_transaction_means,
    get_transaction_medians,
    get_biggest_spending,
    get_transaction_count,
    get_spent_so_far_warning,
)

router = APIRouter()


@router.get("/main-insights/spending-by-month")
def spending_by_month(dataset_id: str = Query(..., description="ID returned by /upload")):
    df = dataset_store.get(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found or expired. Please re-upload the file.")
    result = get_spending_by_month(df)
    return result.reset_index().to_dict(orient="records")


@router.get("/main-insights/spending-by-category")
def spending_by_category(dataset_id: str = Query(..., description="ID returned by /upload")):
    df = dataset_store.get(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found or expired. Please re-upload the file.")
    result = get_spending_by_category(df)
    return result.reset_index().to_dict(orient="records")


@router.get("/main-insights/total-spending")
def total_spending(dataset_id: str = Query(..., description="ID returned by /upload")):
    df = dataset_store.get(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found or expired. Please re-upload the file.")
    return get_total_spending(df).to_dict()


@router.get("/main-insights/transaction-means")
def transaction_means(dataset_id: str = Query(..., description="ID returned by /upload")):
    df = dataset_store.get(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found or expired. Please re-upload the file.")
    return get_transaction_means(df).to_dict()


@router.get("/main-insights/transaction-medians")
def transaction_medians(dataset_id: str = Query(..., description="ID returned by /upload")):
    df = dataset_store.get(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found or expired. Please re-upload the file.")
    return get_transaction_medians(df).to_dict()


@router.get("/main-insights/biggest-spending")
def biggest_spending(
    dataset_id: str = Query(..., description="ID returned by /upload"),
    currency: str = Query("GEL", description="Currency column to sort by (GEL, USD, EUR, GBP)"),
):
    df = dataset_store.get(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found or expired. Please re-upload the file.")
    result = get_biggest_spending(df, currency=currency)
    return result.to_dict(orient="records")


@router.get("/main-insights/transaction-count")
def transaction_count(dataset_id: str = Query(..., description="ID returned by /upload")):
    df = dataset_store.get(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found or expired. Please re-upload the file.")
    return {"count": get_transaction_count(df)}


@router.get("/main-insights/spent-so-far-warning")
def spent_so_far_warning(
    dataset_id: str = Query(..., description="ID returned by /upload"),
    currency: str = Query("GEL", description="Currency column (GEL, USD, EUR, GBP)"),
):
    df = dataset_store.get(dataset_id)
    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found or expired. Please re-upload the file.")
    return {"message": get_spent_so_far_warning(df, currency=currency)}
