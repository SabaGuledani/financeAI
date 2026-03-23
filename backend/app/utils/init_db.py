from app.database.db import engine, Base
from app.models.categories_model import Categories

def create_db():
    try:
        Base.metadata.create_all(bind=engine)
        print("created successfully")
    except Exception as e:
        print(e)
