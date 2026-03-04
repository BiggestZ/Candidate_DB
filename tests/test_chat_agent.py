from backend.agents import chat_agent


def test_is_database_count_query_positive():
    assert chat_agent._is_database_count_query("How many people are in the database?") is True


def test_is_database_count_query_negative():
    assert chat_agent._is_database_count_query("Hello there") is False
    assert chat_agent._is_database_count_query("Find backend engineers in NYC") is False
