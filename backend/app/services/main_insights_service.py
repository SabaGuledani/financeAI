import pandas as pd


def get_spending_by_month(df:pd.DataFrame):
    df["month"] = df["თარიღი"].dt.month
    df["year"] = df["თარიღი"].dt.year
    
    df = df.groupby(["year","month"])[["GEL","USD","EUR","GBP"]].sum()
    return df
def get_spending_by_category(df:pd.DataFrame):
    print(df.columns)
    df = df.groupby(["category"])[["GEL","USD","EUR","GBP"]].sum().sort_values(by="GEL", ascending=False)
    return df

def get_total_spending(df:pd.DataFrame):
    total = df[["GEL","USD","EUR","GBP"]].sum()
    return total

def get_transaction_means(df:pd.DataFrame):
    means = df[["GEL","USD","EUR","GBP"]].mean()
    return means
def get_transaction_medians(df:pd.DataFrame):
    #TODO: make it ignore zeros
    medians = df[["GEL","USD","EUR","GBP"]].median()
    return medians

def get_biggest_spending(df:pd.DataFrame,currency:str="GEL"):
    return df.sort_values(by=currency, ascending=False).head(1)

def get_transaction_count(df:pd.DataFrame):
    count = int(df['თარიღი'].count())
    return count
