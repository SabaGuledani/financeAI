from fastapi import APIRouter, UploadFile, File

from app.services.excel_parser import parse_excel
from app.services.extract_payments import get_payments_df
from app.utils.dataset_store import dataset_store

router = APIRouter()


@router.post("/upload")
async def upload_transactions_excel(file: UploadFile = File(...)):
    transactions_df = parse_excel(file)
    payments_df = get_payments_df(transactions_df)

    transactions_id = dataset_store.put(transactions_df)
    payments_id = dataset_store.put(payments_df)

    return {
        "transactions_id": transactions_id,
        "payments_id": payments_id,
    }
