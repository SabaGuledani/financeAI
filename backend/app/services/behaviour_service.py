
import pandas as pd

def get_spending_by_merchant(df:pd.DataFrame):
    df = df.groupby(["transaction_object"])[["GEL","USD","EUR","GBP"]].sum().sort_values(by="GEL", ascending=False)
    return df

def get_transactions_per_day(df:pd.DataFrame):
    return df.groupby(["თარიღი"])[["GEL"]].count().sort_values(by="GEL", ascending=False)

def get_most_active_day(df:pd.DataFrame):
    return get_transactions_per_day(df).head(1)
