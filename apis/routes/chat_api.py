from fastapi import APIRouter, HTTPException
import os, sys

router = APIRouter(prefix="/chat", tags=['chat'])

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from Chatbot.gen_ai.agents.chat_agent import ChatAgent
from Chatbot.gen_ai.schemas.chat_schema import ChatMessage, ChatResponse
from Chatbot.gen_ai.llm.config import LLMProvider
from Chatbot.gen_ai.agents.types import AgentAction

# Initialize chat agent with default provider (OpenAI)
chat_agent = ChatAgent(LLMProvider.OPENAI)

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
    try:
        # Run the chat agent with the user's message
        result = chat_agent.run(payload.message)

        # Handle unknown intent
        if result.action == AgentAction.UNKNOWN:
            return ChatResponse(
                message=result.message or "I couldn't understand that. Please try again.",
                intent="unknown",
                data=None
            )

        # Handle search results
        if result.action == AgentAction.SEARCH:
            # Convert search results to dict format for JSON response
            candidates_data = None
            if result.data:
                candidates_data = [candidate.model_dump() for candidate in result.data]

            return ChatResponse(
                message=result.message or "",
                intent="search",
                data={"candidates": candidates_data, "count": len(result.data) if result.data else 0}
            )

        # Handle chat response
        return ChatResponse(
            message=result.message or "How can I help you?",
            intent="chat",
            data=None
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")