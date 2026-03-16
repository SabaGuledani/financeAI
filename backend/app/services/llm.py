from google import genai
from dotenv import load_dotenv
import os

load_dotenv('../../backend/.env')
client = genai.Client()
def run_llm(input_prompt, config ):
    response = client.models.generate_content(model="gemini-3-flash-preview",
                                              contents=input_prompt,
                                              config=config)
    return response
