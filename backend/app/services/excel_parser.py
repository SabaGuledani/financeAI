import pandas as pd

def parse_excel(excel_path:str)->pd.DataFrame:

    transactions_df = pd.read_excel("../../data/raw/amonaweri.xlsx", sheet_name="ტრანზაქციები")
    transactions_df.drop(columns=["Unnamed: 2"],inplace=True) # drop unneccessary col
    transactions_df["transaction_type"] = transactions_df["დანიშნულება"].apply(lambda x: x.split()[0]) # separate by transaction type
    return transactions_df