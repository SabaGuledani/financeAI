import pandas as pd

def parse_excel(file) -> pd.DataFrame:

    # FastAPI UploadFile exposes a SpooledTemporaryFile at .file
    file_obj = getattr(file, "file", file)
    transactions_df = pd.read_excel(file_obj, sheet_name="ტრანზაქციები")
    transactions_df.drop(columns=["Unnamed: 2"],inplace=True) # drop unneccessary col
    transactions_df["transaction_type"] = transactions_df["დანიშნულება"].apply(lambda x: x.split()[0]) # separate by transaction type
    transactions_df["თარიღი"] = pd.to_datetime(transactions_df["თარიღი"], dayfirst=True) # convert to datetime for simplicity

    return transactions_df