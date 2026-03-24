import pandas as pd
from sqlalchemy.orm import Session
from app.models.categories_model import Categories
from app.services.llm_service import run_llm_categorization
from app.utils.util_functions import get_eixisting_categories_df, get_unknown_merchants, parse_categorization_response
from app.utils.prompts import categorization_sys_prompt
import requests


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
def categorize_merchants_pipeline(df:pd.DataFrame):
    print("Fetching existing categories dataframe")
    existing_categories_df = get_eixisting_categories_df(df) # fetch existing categories from server
    print("Existing categories dataframe fetched")
    merchants_list = list(df["transaction_object"].unique()) # get all merchants from transactions
    print("Merchants list fetched")
    unknown_merchants = get_unknown_merchants(existing_categories_df, merchants_list) # get whicih merchants have unassigned categories
    print("Unknown merchants fetched")
    if len(unknown_merchants) > 0:
        llm_categories_response = run_llm_categorization(unknown_merchants, categorization_sys_prompt) # run llm to assign categories
        print("LLM categories response fetched")
        categories_df = parse_categorization_response(llm_categories_response) # parse llm response 
        print("Categories dataframe parsed")

        records = categories_df[["merchant", "category", "confidence"]].to_dict(orient="records") # convert to records
        print("Records converted to dictionary")
        response = requests.post("http://localhost:8000/upload-categories", json=records) # upload to server
        print("Categories uploaded to server")

        if response.status_code == 200:
            print("Categories uploaded successfully")
        else:
            print("Failed to upload categories:", response.status_code)
    else:
        print("No unknown merchants found")
        return "no unknown merchants found"