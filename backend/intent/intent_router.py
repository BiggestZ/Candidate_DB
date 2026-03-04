from openai import OpenAI
import json
import os
import re
from dotenv import load_dotenv
from typing import Optional

from backend.llm.prompt_loader import load_prompt, load_keywords
from backend.schema.intent_schema import IntentType, Intent, IntentSource
from backend.schema.search_schema import CandidateSearchParams

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI")

# Load in text files
INTENT_PROMPT = load_prompt("intent/intent.txt")
SEARCH_KEYWORDS = load_keywords("intent/search_keywords.txt")
CHAT_KEYWORDS = {
    "hi", "hello", "hey", "thanks", "thank you", "how are you",
    "what can you do", "help", "who are you",
}
SINGLE_WORD_KEYWORDS = {k for k in SEARCH_KEYWORDS if " " not in k}
PHRASE_KEYWORDS = {k for k in SEARCH_KEYWORDS if " " in k}
KEYWORD_SCORE_THRESHOLD = 0.45
LLM_CONFIDENCE_THRESHOLD = 0.60


def _get_client() -> Optional[OpenAI]:
    if not OPENAI_API_KEY:
        return None
    return OpenAI(api_key=OPENAI_API_KEY)


def _tokenize(message: str) -> set[str]:
    tokens = set(re.findall(r"\b[\w+-]+\b", message.lower()))
    singularized = {
        token[:-1] for token in tokens
        if token.endswith("s") and len(token) > 3
    }
    return tokens | singularized


def _keyword_score(message: str) -> float:
    normalized = message.lower().strip()
    if not normalized:
        return 0.0

    tokens = _tokenize(normalized)
    token_matches = sum(1 for keyword in SINGLE_WORD_KEYWORDS if keyword in tokens)
    phrase_matches = sum(1 for phrase in PHRASE_KEYWORDS if phrase in normalized)
    chat_matches = sum(1 for keyword in CHAT_KEYWORDS if keyword in normalized)

    # Promote multi-signal search intent, but discount clearly conversational messages.
    raw = (token_matches * 0.12) + (phrase_matches * 0.25) - (chat_matches * 0.20)
    return max(0.0, min(1.0, raw))


def _fallback_unknown(reason: str) -> Intent:
    return Intent(
        intent=IntentType.unknown,
        source=IntentSource.fallback,
        confidence=0.0,
        reason=reason,
        search_params=None,
    )


def detect_keywords(user_input: str) -> Optional[Intent]:
    """Keyword-first classifier for high-confidence search detection."""
    message = user_input.strip()
    if not message:
        return None

    score = _keyword_score(message)
    if score >= KEYWORD_SCORE_THRESHOLD:
        return Intent(
            intent=IntentType.search,
            source=IntentSource.keyword,
            confidence=score,
            reason="Matched weighted search keywords.",
            search_params=CandidateSearchParams(
                semantic_query=message,
                filters=None,
                limit=10,
            ),
        )
    return None


def detect_intent(user_input: str) -> Intent:
    message = user_input.strip()
    if not message:
        return _fallback_unknown("Empty user input.")

    keyword_intent = detect_keywords(message)
    if keyword_intent:
        return keyword_intent

    client = _get_client()
    if client is None:
        return _fallback_unknown("OPENAI API key is not configured.")

    try:
        resp = client.responses.create(
            model="gpt-4.1-mini",
            temperature=0.0,
            max_output_tokens=150,
            input=[
                {"role": "system", "content": INTENT_PROMPT},
                {"role": "user", "content": message},
            ],
        )

        raw_text = resp.output_text.strip()
        data = json.loads(raw_text)
        intent = Intent.model_validate(data)

        if intent.confidence < LLM_CONFIDENCE_THRESHOLD:
            return _fallback_unknown(
                f"Low-confidence intent classification ({intent.confidence:.2f})."
            )
        return intent

    except Exception as exc:
        return _fallback_unknown(f"LLM intent detection failed: {type(exc).__name__}")
