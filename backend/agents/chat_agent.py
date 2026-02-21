import os, sys
project_root=os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from agents.base import BaseAgent
from agents.retrieval_agent import RetrievalAgent
from agents.types import AgentAction, AgentResult
from llm.client import LLMClient
from llm.config import LLMProvider, LLMTask
from llm.prompt_loader import load_prompt
from llm.response_parser import parse_llm_json, LLMResponseError
from schema.intent_schema import Intent, IntentType
from evaluator.app_logger import setup_logger

logger = setup_logger(__name__, level=10)  # DEBUG level

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

        try:
            # Load prompt
            logger.debug("Loading intent classification prompt...")
            prompt = load_prompt(
                "intent/intent.txt",
                schema=Intent,
                user_message=user_message
            )
            logger.debug(f"Prompt loaded, length: {len(prompt)} chars")

            # Run LLM given task and prompt
            logger.debug("Calling LLM for intent classification...")
            raw = self.llm.run(
                task=LLMTask.INTENT,
                prompt=prompt
            )
            logger.debug(f"LLM response received: {raw[:200]}...")

            # Parse intent from raw LLM Output
            logger.debug("Parsing LLM response to Intent object...")
            intent = parse_llm_json(raw, Intent)
            logger.info(f"✓ Intent parsed: {intent.intent.value} (confidence: {intent.confidence})")

        except LLMResponseError as e:
            logger.error(f"✗ Failed to parse LLM response: {e}", exc_info=True)
            return AgentResult(
                action=AgentAction.UNKNOWN,
                message="I could not understand the request. Please try again."
            )
        except Exception as e:
            logger.error(f"✗ Unexpected error in intent classification: {e}", exc_info=True)
            return AgentResult(
                action=AgentAction.UNKNOWN,
                message="An error occurred. Please try again."
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