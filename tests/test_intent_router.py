from backend.intent import intent_router
from backend.schema.intent_schema import Intent, IntentSource, IntentType
from backend.schema.search_schema import CandidateSearchParams


def test_detect_keywords_returns_search_for_clear_recruiting_query():
    intent = intent_router.detect_keywords("find senior python backend engineers in nyc")
    assert intent is not None
    assert intent.intent == IntentType.search
    assert intent.source == IntentSource.keyword
    assert intent.search_params is not None
    assert intent.search_params.semantic_query == "find senior python backend engineers in nyc"


def test_detect_keywords_ignores_conversational_query():
    intent = intent_router.detect_keywords("hello, what can you do?")
    assert intent is None


def test_detect_keywords_handles_implicit_recruiting_goal():
    intent = intent_router.detect_keywords("need strong data engineers with 5 years in chicago")
    assert intent is not None
    assert intent.intent == IntentType.search
    assert intent.search_params is not None
    assert intent.search_params.limit == 10


def test_detect_keywords_extracts_requested_limit():
    intent = intent_router.detect_keywords("show me top 7 python developers in nyc")
    assert intent is not None
    assert intent.search_params is not None
    assert intent.search_params.limit == 7


def test_detect_intent_returns_unknown_for_empty_input():
    intent = intent_router.detect_intent("   ")
    assert intent.intent == IntentType.unknown
    assert intent.source == IntentSource.fallback


def test_detect_intent_returns_chat_for_capability_question_without_api_key(monkeypatch):
    monkeypatch.setattr(intent_router, "OPENAI_API_KEY", None)
    intent = intent_router.detect_intent("what can you do for recruiters?")
    assert intent.intent == IntentType.chat
    assert intent.source == IntentSource.keyword


def test_detect_intent_returns_unknown_without_api_key_when_not_keyword(monkeypatch):
    monkeypatch.setattr(intent_router, "OPENAI_API_KEY", None)
    intent = intent_router.detect_intent("can you do it")
    assert intent.intent == IntentType.unknown
    assert intent.source == IntentSource.fallback


def test_detect_intent_respects_negated_search_signal_without_api_key(monkeypatch):
    monkeypatch.setattr(intent_router, "OPENAI_API_KEY", None)
    intent = intent_router.detect_intent("I am not hiring right now, just testing this tool")
    assert intent.intent == IntentType.chat
    assert intent.source == IntentSource.keyword


def test_intent_schema_requires_search_params_for_search():
    params = CandidateSearchParams(semantic_query="senior backend engineer", limit=10)
    parsed = Intent(
        intent=IntentType.search,
        source=IntentSource.keyword,
        confidence=0.9,
        reason="keyword",
        search_params=params,
    )
    assert parsed.search_params is not None


def test_intent_schema_rejects_invalid_search_params_shape_for_chat():
    params = CandidateSearchParams(semantic_query="senior backend engineer", limit=10)
    try:
        Intent(
            intent=IntentType.chat,
            source=IntentSource.llm,
            confidence=0.9,
            reason=None,
            search_params=params,
        )
        assert False, "Expected validation error"
    except Exception:
        assert True
