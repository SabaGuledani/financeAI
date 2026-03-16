import pandas as pd
import re

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
    

    return payments_df
