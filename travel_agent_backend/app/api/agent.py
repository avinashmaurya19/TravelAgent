"""API endpoints for agent intent recognition and natural language dialog orchestration."""

from typing import Optional
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.agent.intents import AgentIntent
from app.agent.intent_engine import IntentEngine
from app.agent.state import TravelState
from app.agent.agent import AgentOrchestrator, AgentResult

router = APIRouter(prefix="/agent", tags=["Agent & Intent Engine"])

# Global IntentEngine instance for intent-only requests
_intent_engine = IntentEngine()


class IntentRecognitionRequest(BaseModel):
    """User prompt request for intent parsing."""
    query: str = Field(..., description="Natural language travel query", min_length=1)
    context: Optional[str] = Field(default=None, description="Optional prior conversation context")


class AgentChatRequest(BaseModel):
    """User prompt request for interactive multi-turn agent execution."""
    message: str = Field(..., description="User chat message or instruction", min_length=1)
    session_id: Optional[str] = Field(default=None, description="Optional session/conversation ID")
    state: Optional[TravelState] = Field(default=None, description="Current structured travel state from client")


@router.post(
    "/intent",
    response_model=AgentIntent,
    status_code=status.HTTP_200_OK,
    summary="Recognize structured travel intent from natural language query",
)
async def recognize_intent(req: IntentRecognitionRequest) -> AgentIntent:
    """Classify user query into an AgentIntent and extract structured travel constraints."""
    intent = await _intent_engine.recognize_intent(query=req.query, context=req.context)
    return intent


import logging

logger = logging.getLogger(__name__)

@router.post(
    "/chat",
    response_model=AgentResult,
    status_code=status.HTTP_200_OK,
    summary="Orchestrate agent reasoning, tool execution, and state persistence for a chat turn",
)
def chat_with_agent(
    req: AgentChatRequest,
    db: Session = Depends(get_db),
) -> AgentResult:
    """Run the AgentOrchestrator loop to answer query, call tools, and return updated state."""
    logger.info("Received user prompt: '%s' | existing state: %s", req.message, req.state)
    orchestrator = AgentOrchestrator(db=db)
    try:
        result = orchestrator.run(
            user_message=req.message,
            state=req.state,
        )
        logger.info("Agent completed turn (tools executed: %d, response length: %d chars)", len(result.tool_trace), len(result.response))
        return result
    except Exception as e:
        logger.error("Agent execution error for prompt '%s': %s", req.message, e, exc_info=True)
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent reasoning failed: {str(e)}",
        )
