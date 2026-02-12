"""File is incharge of embedding text, right now OpenAI specific, will change later (MVP)"""
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI"))

def embed(text: str) -> list[float]:
    if not isinstance(text, str):
        raise TypeError(
            f"embed() expects str, got {type(text)}: {text}"
        )
    text = text.strip()
    if not text:
        raise ValueError("Can't embed empty text.")
        
    resp = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return resp.data[0].embedding