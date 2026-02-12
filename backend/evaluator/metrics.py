"""
This file defines a basic metrics class. Will be expanded in the future.
Future iterations: Prometheus, Grafana, Dashboards
"""
class Metrics:
    """Class of counters for now"""
    llm_calls = 0
    llm_failures = 0
    agent_failures = 0

    @classmethod
    def inc_llm_calls(cls):
        cls.llm_calls += 1
    
    @classmethod
    def inc_llm_fails(cls):
        cls.llm_failures += 1
    
    @classmethod
    def inc_agent_fails(cls):
        cls.agent_failures += 1