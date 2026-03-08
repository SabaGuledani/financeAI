import psycopg2
from dotenv import load_dotenv
import os
from app.utils.init_db import create_db

create_db()