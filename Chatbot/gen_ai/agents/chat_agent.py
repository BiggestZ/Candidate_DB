from agents.base import BaseAgent
from agents.retrieval_agent import RetrievalAgent
from agents.types import AgentAction, AgentResult
from llm.client import LLMClient
from llm.config import LLMProvider, LLMTask
from llm.prompt_loader import load_prompt
from llm.response_parser import parse_llm_json, LLMResponseError
from schemas.search_schema import CandidateSearchIntent

class ChatAgent(BaseAgent): 
    def __init__(self, provider: LLMProvider):
        self.llm = LLMProvider(provider)
        self.retrieval_agent = RetrievalAgent()

    def run(self, user_message: str) -> AgentResult:
        prompt = load_prompt(
            "intent/intent.txt",
            schema=CandidateSearchIntent,
            user_message=user_message
        )

        # Run LLM given task and prompt
        raw = self.llm.run(
            task=LLMTask.INTENT,
            prompt=prompt
        )

        try: 
            # Parse intent from raw LLM Output
            intent = parse_llm_json(raw, CandidateSearchIntent)
        except LLMResponseError:
            return AgentResult(
                action=AgentAction.UNKNOWN,
                message="I could not understadn the request. Please try again."
            )
        # 
        if intent.is_search:
            return self.retrieval_agent.run(intent)
        
        # 
        return AgentResult(
            action=AgentAction.CHAT,
            message="How else can I help?"
        )