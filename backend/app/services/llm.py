
def run_llm(input_prompt, config ):
    response = client.models.generate_content(model="gemini-3-flash-preview",
                                              contents=input_prompt,
                                              config=config)
    return response
