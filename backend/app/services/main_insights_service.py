import pandas as pd
from datetime import datetime

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

def get_spent_so_far_warning(df:pd.DataFrame, currency:str="GEL"):
    today = datetime.today()
    start_of_month = today.replace(day=1)

    # Current month spending
    current_month_df = df[df['თარიღი'] >= start_of_month]
    spent_so_far = current_month_df[currency].sum()
    days_passed = today.day

    median_monthly_spending = get_spending_by_month(df).reset_index()[currency].median()

    percentage = spent_so_far / median_monthly_spending * 100
    expected_percentage = days_passed / 30 * 100
    
    predicted_pace = f"You spent {percentage:.0f}% of your usual monthly spending in the first {days_passed} days."
    if percentage > expected_percentage * 1.3:
        return f"{predicted_pace} At this pace, you may exceed your typical monthly spending. "
    else:
        return f"{predicted_pace} At this pace you are not likely to exceed your typical monthly spending."
def get_monthly_spending_prediction(df:pd.DataFrame, currency:str="GEL"):
    today = datetime.today()
    start_of_month = today.replace(day=1)
    current_month_df = df[df['თარიღი'] >= start_of_month]
    spent_so_far = current_month_df[currency].sum()
    days_passed = today.day
    predicted_total = spent_so_far / days_passed * 30
    return f"You are projected to spend {predicted_total:.0f} {currency} this month."