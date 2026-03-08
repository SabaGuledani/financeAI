from app.database.db import engine, Base
from app.models.transaction_model import Transaction

def create_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("created successfully")
    except Exception as e:
        print(e)
