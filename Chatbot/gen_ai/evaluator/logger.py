from evaluator.storage import write_event
from evaluator.events import LLMEvent, AgentEvent

def log_llm_event(event: LLMEvent):
    write_event(event, "llm_events.jsonl")

def log_agent_event(event: AgentEvent):
    write_event(event, "agent_events.jsonl")