from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.db import get_db
from app.models.categories_model import Categories
from app.services.categories_service import upload_categories
from pydantic import BaseModel
from typing import List
import pandas as pd

router = APIRouter()


class CategoryRecord(BaseModel):
    merchant: str
    category: str
    confidence: str


@router.get("/categories")
def get_all_categories(db: Session = Depends(get_db)):
    return db.query(Categories).all()


@router.post("/upload-categories")
def upload(records: List[CategoryRecord], db: Session = Depends(get_db)):
    df = pd.DataFrame([r.model_dump() for r in records])
    upload_categories(df, db)
    return {"message": f"Uploaded {len(df)} rows"}