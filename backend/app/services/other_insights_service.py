import pandas as pd

def get_anomaly_transactions(df:pd.DataFrame, currency:str="GEL"):
    std = df[currency].std()
    mean = df[currency].mean()
    df_anomaly = df[df[currency] > mean + 2 * std]
    return df_anomaly
    
def get_month_comparison_analysis(latest_month_df, previous_month_biggest_spending_category, currency="GEL"):
    if len(previous_month_biggest_spending_category) != 0:
        percent_difference = ((latest_month_df[currency] - previous_month_biggest_spending_category[currency]) / previous_month_biggest_spending_category[currency]) * 100 if previous_month_biggest_spending_category[currency] != 0 else float('inf')
        
        if percent_difference > 0:
            return f"This month your spending on {latest_month_df["category"]} was more than previous month by {percent_difference}%"
        else:
            return f"This month your spending on {latest_month_df["category"]} was less than previous month by {percent_difference}%"
    else:
        return "No previous month data available"

def get_month_category_comparison(df:pd.DataFrame, currency:str="GEL"):
    df["month"] = df["თარიღი"].dt.month
    df["year"] = df["თარიღი"].dt.year
    df = df.groupby(["year","month","category"])[["GEL","USD","EUR","GBP"]].sum()

    df_reset = df.reset_index()

    latest = df_reset.sort_values(by=["year",'month']).iloc[-1]
    latest_month, latest_year = latest[["month","year"]]

    previous_month = latest_month - 1 if latest_month != 1 else 12

    latest_month_df = df_reset[(df_reset["year"] == latest_year) & (df_reset['month'] == latest_month)]
    previous_month_df = df_reset[(df_reset["year"] == latest_year) & (df_reset['month'] == previous_month)]

    latest_month_df = latest_month_df.sort_values(by=[currency], ascending=False).head(1)
    previous_month_df = previous_month_df.sort_values(by=[currency], ascending=False)
    biggest_spending_category = latest_month_df["category"].values[0]
    previous_month_biggest_spending_category = previous_month_df[previous_month_df["category"] == biggest_spending_category].values
    return get_month_comparison_analysis(latest_month_df, previous_month_biggest_spending_category, currency)


    