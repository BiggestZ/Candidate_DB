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
    "hi",
    "hello",
    "hey",
    "thanks",
    "thank you",
    "how are you",
    "what can you do",
    "help",
    "who are you",
    "how does this work",
    "what does this do",
    "how do i use this",
}
SINGLE_WORD_KEYWORDS = {k for k in SEARCH_KEYWORDS if " " not in k}
PHRASE_KEYWORDS = {k for k in SEARCH_KEYWORDS if " " in k}
SEARCH_ACTIONS = {
    "find", "search", "show", "get", "source", "hire", "recruit", "shortlist",
    "screen", "filter", "match", "locate", "identify", "need", "looking",
}
RECRUITING_ENTITIES = {
    "candidate", "candidates", "applicant", "applicants", "profile", "profiles",
    "resume", "resumes", "talent",
}
ROLE_TERMS = {
    "engineer", "developer", "designer", "manager", "analyst", "architect",
    "consultant", "specialist", "scientist", "recruiter",
}
CONSTRAINT_PATTERNS = (
    r"\b(?:in|from|based in)\s+[a-z][a-z\s-]{1,40}\b",
    r"\b(?:with|having|at least|minimum)\s+\d+\+?\s*(?:years?|yrs?)\b",
    r"\b(?:remote|hybrid|onsite|on-site)\b",
    r"\b(?:senior|junior|principal|staff|lead|mid(?:-level)?)\b",
)
NEGATED_SEARCH_PATTERNS = (
    r"\b(?:not|don't|do not|isn't|is not)\b.{0,20}\b(?:looking for|hiring|recruiting|searching)\b",
    r"\b(?:without searching|not a search)\b",
)

SEARCH_SCORE_THRESHOLD = 0.56
CHAT_SCORE_THRESHOLD = 0.68
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


def _count_token_matches(tokens: set[str], vocabulary: set[str]) -> int:
    return sum(1 for item in vocabulary if item in tokens)


def _extract_requested_limit(message: str) -> int:
    match = re.search(r"\b(?:top|first|show me|give me)\s+(\d{1,2})\b", message.lower())
    if not match:
        return 10
    requested = int(match.group(1))
    return max(1, min(25, requested))


def _has_constraint_signal(message: str) -> bool:
    normalized = message.lower()
    return any(re.search(pattern, normalized) for pattern in CONSTRAINT_PATTERNS)


def _is_negated_search(message: str) -> bool:
    normalized = message.lower()
    return any(re.search(pattern, normalized) for pattern in NEGATED_SEARCH_PATTERNS)


def _search_score(message: str) -> float:
    normalized = message.lower().strip()
    if not normalized:
        return 0.0

    tokens = _tokenize(normalized)
    action_matches = _count_token_matches(tokens, SEARCH_ACTIONS)
    entity_matches = _count_token_matches(tokens, RECRUITING_ENTITIES)
    role_matches = _count_token_matches(tokens, ROLE_TERMS)
    token_matches = _count_token_matches(tokens, SINGLE_WORD_KEYWORDS)
    phrase_matches = sum(1 for phrase in PHRASE_KEYWORDS if phrase in normalized)
    constraint_bonus = 1 if _has_constraint_signal(normalized) else 0
    chat_penalty = sum(1 for keyword in CHAT_KEYWORDS if keyword in normalized)

    # Multi-signal scoring biased toward user goal semantics, not raw keyword count.
    raw = (
        (action_matches * 0.30)
        + (entity_matches * 0.25)
        + (role_matches * 0.20)
        + (token_matches * 0.06)
        + (phrase_matches * 0.18)
        + (constraint_bonus * 0.12)
        - (chat_penalty * 0.22)
    )
    if _is_negated_search(normalized):
        raw -= 0.45

    return max(0.0, min(1.0, raw))


def _chat_score(message: str) -> float:
    normalized = message.lower().strip()
    if not normalized:
        return 0.0

    tokens = _tokenize(normalized)
    greeting = 1 if re.search(r"^(hi|hello|hey)\b", normalized) else 0
    help_question = 1 if any(phrase in normalized for phrase in CHAT_KEYWORDS) else 0
    direct_capability = 1 if re.search(r"\b(can you|could you|how do i|what can)\b", normalized) else 0
    search_drag = (
        _count_token_matches(tokens, SEARCH_ACTIONS)
        + _count_token_matches(tokens, ROLE_TERMS)
        + _count_token_matches(tokens, RECRUITING_ENTITIES)
    )

    raw = (greeting * 0.45) + (help_question * 0.45) + (direct_capability * 0.20) - (search_drag * 0.14)
    if _is_negated_search(normalized):
        raw += 0.25
    return max(0.0, min(1.0, raw))


def _is_meta_capability_query(message: str) -> bool:
    normalized = message.lower().strip()
    if re.search(r"^(what can you do|how does this work|how do i use this)\b", normalized):
        return True
    if "what features" in normalized or "help me use" in normalized:
        return True
    return False


def _fallback_unknown(reason: str) -> Intent:
    return Intent(
        intent=IntentType.unknown,
        source=IntentSource.fallback,
        confidence=0.0,
        reason=reason,
        search_params=None,
    )


def detect_keywords(user_input: str) -> Optional[Intent]:
    """Local high-confidence classifier for clear search intent."""
    message = user_input.strip()
    if not message:
        return None

    search_score = _search_score(message)
    chat_score = _chat_score(message)
    if search_score >= SEARCH_SCORE_THRESHOLD and (search_score - chat_score) >= 0.12:
        return Intent(
            intent=IntentType.search,
            source=IntentSource.keyword,
            confidence=search_score,
            reason="High-confidence recruiting/search intent from multi-signal routing.",
            search_params=CandidateSearchParams(
                semantic_query=message,
                filters=None,
                limit=_extract_requested_limit(message),
            ),
        )
    return None


def _detect_local_chat(user_input: str) -> Optional[Intent]:
    message = user_input.strip()
    if not message:
        return None

    if _is_meta_capability_query(message):
        return Intent(
            intent=IntentType.chat,
            source=IntentSource.keyword,
            confidence=0.9,
            reason="Meta/system capability question.",
            search_params=None,
        )

    search_score = _search_score(message)
    chat_score = _chat_score(message)
    if chat_score >= CHAT_SCORE_THRESHOLD and (chat_score - search_score) >= 0.10:
        return Intent(
            intent=IntentType.chat,
            source=IntentSource.keyword,
            confidence=chat_score,
            reason="High-confidence conversational intent from local routing.",
            search_params=None,
        )
    return None


def _extract_json_object(raw_text: str) -> str:
    text = raw_text.strip()
    if text.startswith("{") and text.endswith("}"):
        return text
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        return text[start : end + 1]
    return text


def detect_intent(user_input: str) -> Intent:
    message = user_input.strip()
    if not message:
        return _fallback_unknown("Empty user input.")

    keyword_intent = detect_keywords(message)
    if keyword_intent:
        return keyword_intent

    local_chat_intent = _detect_local_chat(message)
    if local_chat_intent:
        return local_chat_intent

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

        raw_text = _extract_json_object(resp.output_text)
        data = json.loads(raw_text)
        intent = Intent.model_validate(data)

        if intent.confidence < LLM_CONFIDENCE_THRESHOLD:
            # Use best local interpretation if LLM is uncertain.
            local_search = detect_keywords(message)
            if local_search:
                return local_search

            local_chat = _detect_local_chat(message)
            if local_chat:
                return local_chat

            return _fallback_unknown(
                f"Low-confidence intent classification ({intent.confidence:.2f})."
            )
        return intent

    except Exception as exc:
        return _fallback_unknown(f"LLM intent detection failed: {type(exc).__name__}")
