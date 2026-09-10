from langchain_openai import ChatOpenAI

import streamlit as st

try:
    api_key = st.secrets["OPENAI_API_KEY"]

    if not api_key:
        raise ValueError("OPENAI_API_KEY is not configured.")
    
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7,
        api_key = api_key
    )
except Exception as e:
    print(f"OpenAI initialization failed: {e}")
    llm = None