"""API endpoints for agent intent recognition and natural language parsing."""

from typing import Optional
from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.agent.intents import AgentIntent
from app.agent.intent_engine import IntentEngine

router = APIRouter(prefix="/agent", tags=["Agent & Intent Engine"])

# Global IntentEngine instance
_intent_engine = IntentEngine()


class IntentRecognitionRequest(BaseModel):
    """User prompt request for intent parsing."""
    query: str = Field(..., description="Natural language travel query", min_length=1)
    context: Optional[str] = Field(default=None, description="Optional prior conversation context")


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
