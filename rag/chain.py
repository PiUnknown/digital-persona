import os
from groq import Groq
from dotenv import load_dotenv
from rag.retriever import retrieve_chunks

load_dotenv()

import streamlit as st

api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")
client = Groq(api_key=api_key)

SYSTEM_PROMPT = """You are an AI assistant that answers questions about a person 
based strictly on their profile data provided to you as context.

Rules:
- Only answer from the context given. 
- If something isn't in the context, say "I don't have that information."
- Keep answers concise and professional.
- Never make things up."""


def ask(query: str, index, chunks: list[str], chat_history: list[dict]) -> str:
    context = "\n\n".join(retrieve_chunks(query, index, chunks))

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += chat_history
    messages.append({
        "role": "user",
        "content": f"Context:\n{context}\n\nQuestion: {query}"
    })

    resp = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.3,
        max_tokens=1000
    )

    return resp.choices[0].message.content