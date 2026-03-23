import re
import json
import ast
import pandas as pd
def clean_response(text, parse_as="json"):
    """
    Cleans LLM output by removing code fences and parses it.
    
    Args:
        text (str): The LLM response text.
        parse_as (str): "json" or "python". Determines parser.
        
    Returns:
        Parsed Python object (dict/list/etc.).
    """
    # Remove ```json, ```python, or ``` code fences
    cleaned = re.sub(r'```(?:json|python)?', '', text).strip()
    
    if parse_as == "json":
        return json.loads(cleaned)
    elif parse_as == "python":
        return ast.literal_eval(cleaned)
    else:
        raise ValueError("parse_as must be 'json' or 'python'")

def parse_categorization_response(response):
    try:
        response_text = response.text
        response_text = clean_response(response_text, parse_as="json")
        print(response_text)
        categories_df = pd.DataFrame(response_text["results"])
    except Exception as e:
        print(f"Error parsing categorization response: {e}")
        return None

    return categories_df

def get_unknown_merchants(merchants_df:pd.DataFrame, merchants_list:list):
    existing_merchants = list(merchants_df["merchant"].unique())
    merchants_list = [merchant for merchant in merchants_list if merchant not in existing_merchants]
    return merchants_list 