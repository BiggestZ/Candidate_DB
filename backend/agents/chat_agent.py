from backend.agents.base import BaseAgent
from backend.agents.retrieval_agent import RetrievalAgent
from backend.agents.types import AgentAction, AgentResult
from backend.llm.client import LLMClient
from backend.llm.config import LLMProvider, LLMTask
from backend.llm.prompt_loader import load_prompt
from backend.intent.intent_router import detect_intent
from backend.schema.intent_schema import IntentType
from backend.service.candidate_stats import get_candidate_count
from backend.evaluator.app_logger import setup_logger
import re

logger = setup_logger(__name__, level=10)  # DEBUG level


def _is_database_count_query(user_message: str) -> bool:
    normalized = user_message.lower()
    has_count_phrase = bool(
        re.search(r"\b(how many|number of|count)\b", normalized)
    )
    has_subject = bool(
        re.search(r"\b(candidates?|people|profiles?)\b", normalized)
    )
    has_scope = bool(
        re.search(r"\b(database|db|in (the )?system|in total)\b", normalized)
    )
    return has_count_phrase and has_subject and has_scope

class ChatAgent(BaseAgent):
    def __init__(self, provider: LLMProvider):
        logger.info(f"Initializing ChatAgent with provider: {provider.value}")
        try:
            self.llm = LLMClient(provider)
            self.retrieval_agent = RetrievalAgent()
            logger.info("✓ ChatAgent components initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize ChatAgent components: {e}", exc_info=True)
            raise

    def run(self, user_message: str) -> AgentResult:
        logger.info(f"🤖 ChatAgent.run() called with message: '{user_message[:100]}...'")

        if _is_database_count_query(user_message):
            logger.info("📊 Candidate count query detected")
            try:
                total = get_candidate_count()
                noun = "candidate" if total == 1 else "candidates"
                return AgentResult(
                    action=AgentAction.CHAT,
                    message=f"There are currently {total} {noun} in the database."
                )
            except Exception as e:
                logger.error(f"✗ Failed to fetch candidate count: {e}", exc_info=True)
                return AgentResult(
                    action=AgentAction.CHAT,
                    message="I can't access database counts right now. Please try again shortly."
                )

        try:
            logger.debug("Detecting intent via unified intent router...")
            intent = detect_intent(user_message)
            logger.info(f"✓ Intent parsed: {intent.intent.value} (confidence: {intent.confidence})")
        except Exception as e:
            logger.error(f"✗ Unexpected error in intent classification: {e}", exc_info=True)
            return AgentResult(
                action=AgentAction.UNKNOWN,
                message="An error occurred. Please try again."
            )

        if intent.intent == IntentType.unknown:
            logger.info("❓ Unknown/ambiguous intent detected")
            return AgentResult(
                action=AgentAction.UNKNOWN,
                message="I wasn't fully sure what you meant. Ask a recruiting question like 'find senior Python engineers in NYC' or ask a general assistant question."
            )

        # If intent is search, run retrieval agent
        if intent.intent == IntentType.search:
            logger.info("🔍 Search intent detected, delegating to RetrievalAgent...")
            return self.retrieval_agent.run(intent)

        # Otherwise, generate chat response
        logger.info("💬 Chat intent detected, generating conversational response")
        try:
            logger.debug("Loading chat prompt...")
            chat_prompt = load_prompt(
                "chat/recruiter_assistant.txt",
                user_message=user_message
            )
            logger.debug(f"Chat prompt loaded, length: {len(chat_prompt)} chars")

            logger.debug("Calling LLM for chat response...")
            chat_response = self.llm.run(
                task=LLMTask.CHAT,
                prompt=chat_prompt
            )
            logger.info(f"✓ Chat response generated: {chat_response[:100]}...")

            return AgentResult(
                action=AgentAction.CHAT,
                message=chat_response
            )
        except Exception as e:
            logger.error(f"✗ Failed to generate chat response: {e}", exc_info=True)
            return AgentResult(
                action=AgentAction.CHAT,
                message="I apologize, but I'm having trouble generating a response right now. Please try again."
            )
