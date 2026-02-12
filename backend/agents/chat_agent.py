import os, sys
project_root=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# print(project_root)
sys.path.insert(0, project_root)

from agents.base import BaseAgent
from agents.retrieval_agent import RetrievalAgent
from agents.types import AgentAction, AgentResult
from llm.client import LLMClient
from llm.config import LLMProvider, LLMTask
from llm.prompt_loader import load_prompt
from llm.response_parser import parse_llm_json, LLMResponseError
from schema.intent_schema import Intent, IntentType

class ChatAgent(BaseAgent):
    def __init__(self, provider: LLMProvider):
        self.llm = LLMClient(provider)
        self.retrieval_agent = RetrievalAgent()

    def run(self, user_message: str) -> AgentResult:
        prompt = load_prompt(
            "intent/intent.txt",
            schema=Intent,
            user_message=user_message
        )

        # Run LLM given task and prompt
        raw = self.llm.run(
            task=LLMTask.INTENT,
            prompt=prompt
        )

        try:
            # Parse intent from raw LLM Output
            intent = parse_llm_json(raw, Intent)
        except LLMResponseError:
            return AgentResult(
                action=AgentAction.UNKNOWN,
                message="I could not understand the request. Please try again."
            )

        # If intent is search, run retrieval agent
        if intent.intent == IntentType.search:
            return self.retrieval_agent.run(intent)

        # Otherwise, return chat response
        return AgentResult(
            action=AgentAction.CHAT,
            message="How else can I help?"
        )