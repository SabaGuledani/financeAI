from fastapi import FastAPI

from app.api.routes_upload import router as upload_router
from app.api.routes_transactions import router as transactions_router

app = FastAPI()

app.include_router(upload_router)
app.include_router(transactions_router)
