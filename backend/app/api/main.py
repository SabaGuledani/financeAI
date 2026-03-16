from fastapi import FastAPI

from app.api.routes_upload import router as upload_router
from app.api.routes_transactions import router as transactions_router
from dotenv import load_dotenv
from google import genai

load_dotenv('../../backend/.env')
client = genai.Client()

app = FastAPI()

app.include_router(upload_router)
app.include_router(transactions_router)
