from fastapi import APIRouter, UploadFile, File, Depends
from app.services.excel_parser import parse_excel
from app.services.extract_payments import get_payments_df
# from app.database.db import get_db

router = APIRouter()

@router.post("/upload_transactions_excel")
async def upload_transactions_excel(file:UploadFile=File(...)):
    
    df = parse_excel(file)
    df.to_csv('./df.csv', index=False)

    return {"message": "transactions uploaded successfully"}


