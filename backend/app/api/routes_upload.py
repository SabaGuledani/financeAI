from fastapi import APIRouter, UploadFile, File, Depends
from app.services.excel_parser import parse_excel
from app.services.extract_payments import get_payments_df
# from app.database.db import get_db

router = APIRouter()

@router.post("/")
async def upload_transactions_excel(file:UploadFile=File(...)):
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    df = parse_excel(temp_path)
    df.to_csv(f"/tmp/{file.filename.replace("xlsx", "csv")}", index=False)
    return {"message": "transactions uploaded successfully"}


