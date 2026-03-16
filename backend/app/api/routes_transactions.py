from fastapi import APIRouter, HTTPException, Query

from app.utils.dataset_store import dataset_store

router = APIRouter()


@router.get("/transactions")
def get_transactions(dataset_id: str = Query(..., description="ID returned by /upload")):
    df = dataset_store.get(dataset_id)

    if df is None:
        raise HTTPException(status_code=404, detail="Dataset not found or expired. Please re-upload the file.")

    return df.to_dict(orient="records")
