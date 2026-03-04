from fastapi import APIRouter, HTTPException
import traceback

router = APIRouter(prefix="/chat", tags=['chat'])

from backend.agents.chat_agent import ChatAgent
from backend.schema.chat_schema import ChatMessage, ChatResponse
from backend.llm.config import LLMProvider
from backend.agents.types import AgentAction
from backend.evaluator.app_logger import setup_logger

# Set up logging
logger = setup_logger(__name__, level=10)  # DEBUG level

# Initialize chat agent with default provider (OpenAI) - Add future changeability
logger.info("Initializing ChatAgent with OpenAI provider")
try:
    chat_agent = ChatAgent(LLMProvider.OPENAI)
    logger.info("✓ ChatAgent initialized successfully")
except Exception as e:
    logger.error(f"✗ Failed to initialize ChatAgent: {e}", exc_info=True)
    raise

@router.post("", response_model=ChatResponse)
async def chat(payload: ChatMessage):
    """
    Main chat endpoint - all user input starts here.

    Flow:
    1. Receives user message
    2. ChatAgent classifies intent (search vs chat)
    3. If SEARCH: retrieves candidates and returns them with a message
    4. If CHAT: returns a conversational response
    """
    logger.info(f"📨 Received chat request: '{payload.message[:100]}...'")

    try:
        # Run the chat agent with the user's message
        logger.debug("🤖 Running ChatAgent...")
        result = chat_agent.run(payload.message)
        logger.info(f"✓ ChatAgent returned action: {result.action.value}")

        # Handle unknown intent
        if result.action == AgentAction.UNKNOWN:
            logger.warning(f"⚠️ Unknown intent detected: {result.message}")
            return ChatResponse(
                message=result.message or "I couldn't understand that. Please try again.",
                intent="unknown",
                data=None
            )

        # Handle search results
        if result.action == AgentAction.SEARCH:
            result_count = len(result.data) if result.data else 0
            logger.info(f"🔍 Search action - found {result_count} candidates")

            # Convert search results to dict format for JSON response
            candidates_data = None
            if result.data:
                logger.debug(f"Converting {len(result.data)} candidates to dict format")
                candidates_data = [candidate.model_dump() for candidate in result.data]

            response = ChatResponse(
                message=result.message or "",
                intent="search",
                data={"candidates": candidates_data, "count": result_count}
            )
            logger.info(f"✓ Returning search response with {result_count} candidates")
            return response

        # Handle chat response
        logger.info("💬 Chat action - returning conversational response")
        return ChatResponse(
            message=result.message or "How can I help you?",
            intent="chat",
            data=None
        )

    except Exception as e:
        logger.error(f"❌ ERROR in chat endpoint: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        logger.error(f"Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")
