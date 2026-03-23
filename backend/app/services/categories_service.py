import pandas as pd
from sqlalchemy.orm import Session
from app.models.categories_model import Categories


def upload_categories(df: pd.DataFrame, db: Session):
    try:
        records = [
            Categories(
                merchant=row["merchant"],
                category=row["category"],
                confidence=row["confidence"],
            )
            for _, row in df.iterrows()
        ]
        db.add_all(records)
        db.commit()
        print(f"Uploaded {len(records)} rows to categories table")
    except Exception as e:
        db.rollback()
        raise e
