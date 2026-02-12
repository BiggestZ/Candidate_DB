import os, sys
project_root=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# print(project_root)
sys.path.insert(0, project_root)

from agents.base import BaseAgent
from retrieval.search import search_candidates
from schema.intent_schema import Intent
from agents.types import AgentAction, AgentResult

class RetrievalAgent(BaseAgent):
    def run(self, intent: Intent) -> AgentResult:
        # Extract search params from intent
        if not intent.search_params:
            return AgentResult(
                action=AgentAction.SEARCH_CANDIDATES,
                data=[],
                message="No search parameters provided."
            )

        results = search_candidates(
            query=intent.search_params.semantic_query,
            filters=intent.search_params.filters,
            limit=intent.search_params.limit
        )

        # Format response message based on results
        if not results:
            message = "DB is currently empty"
        else:
            message = f"Found {len(results)} candidate(s) matching your search"

        return AgentResult(
            action=AgentAction.SEARCH_CANDIDATES,
            data=results,
            message=message
        )