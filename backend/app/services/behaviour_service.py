
import pandas as pd

WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def get_spending_by_merchant(df:pd.DataFrame):
    df = df.groupby(["transaction_object"])[["GEL","USD","EUR","GBP"]].sum().sort_values(by="GEL", ascending=False)
    return df

def get_transactions_per_day(df:pd.DataFrame):
    return df.groupby(["თარიღი"])[["GEL"]].count().sort_values(by="GEL", ascending=False)

def get_most_active_day(df:pd.DataFrame):
    return get_transactions_per_day(df).head(1)

def get_avg_spending_by_weekday(df:pd.DataFrame):
    df = df.copy()
    df["weekday"] = df["თარიღი"].dt.dayofweek  # 0=Monday, 6=Sunday
    avg = df.groupby("weekday")[["GEL","USD","EUR","GBP"]].mean()
    avg = avg.reindex(range(7), fill_value=0)
    avg["weekday_name"] = WEEKDAY_NAMES
    return avg.reset_index()
