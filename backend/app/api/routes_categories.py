from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.services.categories_service import upload_categories
from typing import List
import pandas as pd
from app.schemas.category_schema import CategoryRecord

router = APIRouter()


@router.post("/upload-categories")
def upload(records: List[CategoryRecord], db: Session = Depends(get_db)):
    df = pd.DataFrame([r.model_dump() for r in records])
    upload_categories(df, db)
    return {"message": f"Uploaded {len(df)} rows"}