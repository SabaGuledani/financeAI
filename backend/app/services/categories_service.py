import pandas as pd
from sqlalchemy.orm import Session
from app.models.categories_model import Categories
from app.services.llm_service import run_llm_categorization
from app.utils.util_functions import get_eixisting_categories_df, get_unknown_merchants, parse_categorization_response
from app.utils.prompts import categorization_sys_prompt
from app.database.db import SessionLocal


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

def categorize_merchants_pipeline(df: pd.DataFrame):
    print("Fetching existing categories dataframe")
    existing_categories_df = get_eixisting_categories_df(df)
    print("Existing categories dataframe fetched")
    merchants_list = list(df["transaction_object"].unique())
    print("Merchants list fetched")
    unknown_merchants = get_unknown_merchants(existing_categories_df, merchants_list)
    print("Unknown merchants fetched")
    if len(unknown_merchants) > 0:
        categories_df = None
        try:
            llm_categories_response = run_llm_categorization(unknown_merchants, categorization_sys_prompt)
            print("LLM categories response fetched")
            categories_df = parse_categorization_response(llm_categories_response)
            print("Categories dataframe parsed")
        except Exception as e:
            print(f"LLM categorization failed ({e}) — falling back to 'other' for unknown merchants")

        if categories_df is None:
            print("Assigning 'other' category to all unrecognised merchants as fallback")
            categories_df = pd.DataFrame([
                {"merchant": m, "category": "other", "confidence": 0.0}
                for m in unknown_merchants
            ])

        db = SessionLocal()
        try:
            upload_categories(categories_df, db)
            print("Categories uploaded successfully")
        finally:
            db.close()
    else:
        print("No unknown merchants found")
        return "no unknown merchants found"