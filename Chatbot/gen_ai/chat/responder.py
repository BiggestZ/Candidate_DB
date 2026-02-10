from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

client = OpenAI()

# What should be said if intent is "CHAT"
def chatResponse():
    pass

# What should be said if intent is "SEARCH"
# PARAMS: The returned context from the RAG SEARCH