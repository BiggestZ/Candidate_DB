from agents.base import BaseAgent
from retriever.search import search_candidates # Not implemented yet
from schemas.search_intent import CandidateSearchIntent
from agents.types import AgentAction, AgentResult

class RetrievalAgent(BaseAgent):
    def run(self, intent: CandidateSearchIntent) -> AgentResult:
        results = search_candidates(
            query= intent.query,
            filters=intent.filters,
            limit=intent.limit
        )
        return AgentResult(
            action=AgentAction.SEARCH_CANDIDATES,
            data=results
        )