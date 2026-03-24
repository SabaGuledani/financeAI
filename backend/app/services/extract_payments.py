import pandas as pd
import re
from app.utils.util_functions import get_eixisting_categories_df
from app.services.categories_service import categorize_merchants_pipeline

def get_payments_df(transactions_df:pd.DataFrame) -> pd.DataFrame:
    """separates actual payments from just transactions"""
    def find_transaction_object(text):
        pattern = r"ობიექტი:\s*([^,]+)"
        res = re.search(pattern, text)
        if res:
            return res.group(1)
    
    payments_df = transactions_df.loc[transactions_df["transaction_type"] == "გადახდა"] # separate actal payments from transactions
    payments_df["transaction_object"] = payments_df["დანიშნულება"].apply(lambda x:find_transaction_object(x) ) # separate where transaction was actually performed
    payments_df["transaction_object"] = payments_df["transaction_object"].fillna(value="gadakhda") # fill wherever object was unavailable
    for currency in ["GEL","USD","EUR","GBP"]:
        payments_df[currency] = payments_df[currency].apply(lambda x: x * -1)
    payments_df.drop(columns=["transaction_type"],inplace=True)
    payments_df.fillna(value=0, inplace=True) # fill other NaN values
    payments_df["transaction_object"] = payments_df["transaction_object"].apply(lambda x: x.lower()) # convert to lowercase
    print("Categorizing merchants pipeline started")
    categorize_merchants_pipeline(payments_df)
    print("Categorizing merchants pipeline completed")
    existing_categories_df = get_eixisting_categories_df(payments_df)
    print("Existing categories dataframe fetched")
    if not existing_categories_df.empty:
        existing_categories_df.rename(columns={"merchant": "transaction_object"}, inplace=True)
        payments_df = pd.merge(payments_df, existing_categories_df, on="transaction_object", how="left")
        payments_df.drop(columns=["confidence"], inplace=True)
    print("Merging existing categories dataframe with payments dataframe")
    return payments_df
