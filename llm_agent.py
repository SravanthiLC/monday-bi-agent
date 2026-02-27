import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ask_llm(system_prompt, user_query):
    # We use 'gemma-3-12b-it' as it is the most stable free model right now
    model = genai.GenerativeModel('gemma-3-12b-it')
    
    # Combine system_prompt and user_query into one single prompt
    # This avoids the '400 Developer instruction' error
    full_prompt = f"{system_prompt}\n\nUSER QUESTION: {user_query}"
    
    try:
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"LLM Error: {str(e)}"