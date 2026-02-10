from enum import Enum
from openai import OpenAI
import os, sys, json
from dotenv import load_dotenv
from typing import Optional

project_root=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
#print(project_root)
sys.path.insert(0, project_root)

from llm.prompt_loader import load_prompt, load_keywords
from schemas.intent_schema import IntentType, Intent, IntentSource

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI"))

# Load in text files
INTENT_PROMPT = load_prompt("intent/intent.txt")
SEARCH_KEYWORDS = load_keywords("intent/search_keywords.txt")

def detect_keywords(user_input: str) -> Optional[Intent]:
    """Keyword classification, if ambigious return None."""
    message = user_input.lower()

    if any(keyword in message for keyword in SEARCH_KEYWORDS):
        return Intent(
            intent=IntentType.search,
            source=IntentSource.keyword,
            confidence=0.9,
            reason="Matched Keyword Search."
        )
    return None

def detect_intent(user_input: str) -> Intent:
    try:
        resp = client.responses.create(
            model="gpt-4.1-mini",
            temperature=0.0,
            max_output_tokens=150,
            input=[
                {"role": "system", "content": INTENT_PROMPT},
                {"role": "user", "content": user_input},
            ],
        )

        raw_text= resp.output_text.strip()

        # DEBUG: Print raw response
        print("=== RAW RESPONSE ===")
        print(raw_text)
        print("=== END RESPONSE ===")

        data = json.loads(raw_text)
        return Intent.model_validate(data)

    except Exception as e:
        print("Intent detection failed: ", e)
        return Intent(
            intent=IntentType.chat,
            source=IntentSource.llm,
            confidence=0.0,
            reason="LLM intent detection failed."
)
