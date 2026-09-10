from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
import os

load_dotenv()

try:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured.")
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7
    )
except Exception as e:
    print(f"OpenAI initialization failed: {e}")
    llm = None