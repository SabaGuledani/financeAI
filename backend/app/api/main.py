import psycopg2
from dotenv import load_dotenv
import os
from app.utils.init_db import create_db
from fastapi import FastAPI
from app.api.routes_upload import router

create_db()

app = FastAPI()
