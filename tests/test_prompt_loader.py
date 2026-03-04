from backend.llm.prompt_loader import load_keywords, load_prompt


def test_load_prompt_renders_template_variables():
    rendered = load_prompt("intent/intent.txt", user_message="Find Python engineers")
    assert "Find Python engineers" in rendered


def test_load_keywords_returns_non_empty_list():
    keywords = load_keywords("intent/search_keywords.txt")
    assert isinstance(keywords, list)
    assert len(keywords) > 0
