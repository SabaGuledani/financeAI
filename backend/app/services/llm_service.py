from google import genai
import os

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def run_llm_categorization(merchants, categorization_sys_prompt):
    merchants_formatted = "\n".join(f"{i+1}. {m}" for i, m in enumerate(merchants))

    config = genai.types.GenerateContentConfig(
        system_instruction=categorization_sys_prompt
    )
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=merchants_formatted,
        config=config,
    )
    return response
