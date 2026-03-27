import pandas as pd

def get_full_dataframe(df: pd.DataFrame):
    return df

def get_anomaly_transactions(df: pd.DataFrame, currency: str = "GEL"):
    std = df[currency].std()
    mean = df[currency].mean()
    df_anomaly = df[df[currency] > mean + 2 * std]
    return df_anomaly

def get_month_comparison_analysis(latest_month_row: pd.Series, previous_month_row, currency: str = "GEL"):
    if previous_month_row is not None:
        prev_val = previous_month_row[currency]
        curr_val = latest_month_row[currency]
        category = latest_month_row["category"]
        percent_difference = ((curr_val - prev_val) / prev_val) * 100 if prev_val != 0 else float("inf")

        if percent_difference > 0:
            return f"This month your spending on {category} was more than previous month by {percent_difference:.1f}%"
        else:
            return f"This month your spending on {category} was less than previous month by {abs(percent_difference):.1f}%"
    else:
        return "No previous month data available"

def get_month_category_comparison(df: pd.DataFrame, currency: str = "GEL"):
    df = df.copy()
    df["month"] = df["თარიღი"].dt.month
    df["year"] = df["თარიღი"].dt.year
    df = df.groupby(["year", "month", "category"])[["GEL", "USD", "EUR", "GBP"]].sum()

    df_reset = df.reset_index()

    latest = df_reset.sort_values(by=["year", "month"]).iloc[-1]
    latest_month = int(latest["month"])
    latest_year = int(latest["year"])

    previous_month = latest_month - 1 if latest_month != 1 else 12
    previous_year = latest_year if latest_month != 1 else latest_year - 1

    latest_month_df = df_reset[(df_reset["year"] == latest_year) & (df_reset["month"] == latest_month)]
    previous_month_df = df_reset[(df_reset["year"] == previous_year) & (df_reset["month"] == previous_month)]

    latest_month_df = latest_month_df.sort_values(by=[currency], ascending=False)
    biggest_spending_category = latest_month_df["category"].values[0]
    latest_month_row = latest_month_df.iloc[0]

    prev_match = previous_month_df[previous_month_df["category"] == biggest_spending_category]
    previous_month_row = prev_match.iloc[0] if not prev_match.empty else None

    return get_month_comparison_analysis(latest_month_row, previous_month_row, currency)


    