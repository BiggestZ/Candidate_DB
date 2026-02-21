import os, sys
project_root=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from agents.base import BaseAgent
from retrieval.search import search_candidates
from schema.intent_schema import Intent
from agents.types import AgentAction, AgentResult
from evaluator.app_logger import setup_logger

logger = setup_logger(__name__, level=10)  # DEBUG level

class RetrievalAgent(BaseAgent):
    def run(self, intent: Intent) -> AgentResult:
        logger.info("🔍 RetrievalAgent.run() called")

        # Extract search params from intent
        if not intent.search_params:
            logger.warning("⚠️ No search parameters provided in intent")
            return AgentResult(
                action=AgentAction.SEARCH_CANDIDATES,
                data=[],
                message="No search parameters provided."
            )

        logger.debug(f"Search params: query='{intent.search_params.semantic_query}', "
                    f"filters={intent.search_params.filters}, limit={intent.search_params.limit}")

        try:
            logger.debug("Calling search_candidates()...")
            results = search_candidates(
                query=intent.search_params.semantic_query,
                filters=intent.search_params.filters,
                limit=intent.search_params.limit
            )
            logger.info(f"✓ Search completed: {len(results)} results found")

        except Exception as e:
            logger.error(f"✗ Error during candidate search: {e}", exc_info=True)
            return AgentResult(
                action=AgentAction.SEARCH_CANDIDATES,
                data=[],
                message="An error occurred during search. Please try again."
            )

        # Format response message based on results
        if not results:
            message = "DB is currently empty"
            logger.info("📭 No results found")
        else:
            message = f"Found {len(results)} candidate(s) matching your search"
            logger.info(f"📦 Returning {len(results)} candidates")

        return AgentResult(
            action=AgentAction.SEARCH,
            data=results,
            message=message
        )