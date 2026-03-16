from fastapi import APIRouter, HTTPException, Query

from app.utils.dataset_store import dataset_store

router = APIRouter()

@router.get("/summary")
def get_summary(dataset_id:str = Query(..., description="ID returned by /upload")):
    pass
