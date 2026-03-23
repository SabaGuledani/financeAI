from fastapi import FastAPI

from app.api.routes_upload import router as upload_router
from app.api.routes_transactions import router as transactions_router
from app.api.routes_main_insights import router as main_insights_router
from app.api.routes_behaviour import router as behaviour_router
from app.api.routes_other_insights import router as other_insights_router
from app.api.routes_summary import router as summary_router
from dotenv import load_dotenv
import os
from pathlib import Path
from google import genai

load_dotenv(Path(__file__).parent.parent.parent / ".env")
client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

app = FastAPI(title="FinanceAI API")

app.include_router(upload_router)
app.include_router(transactions_router)
app.include_router(main_insights_router)
app.include_router(behaviour_router)
app.include_router(other_insights_router)
app.include_router(summary_router)
