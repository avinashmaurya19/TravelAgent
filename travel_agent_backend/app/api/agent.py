"""API endpoints for agent intent recognition and natural language dialog orchestration."""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.agent.intents import AgentIntent
from app.agent.intent_engine import IntentEngine
from app.agent.state import TravelState
from app.agent.agent import AgentOrchestrator, AgentResult
from app.llm.base import ChatMessage

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
    user_id: Optional[str] = Field(default=None, description="Optional user ID for preferences and history")
    state: Optional[TravelState] = Field(default=None, description="Current structured travel state from client")
    chat_history: Optional[List[Dict[str, str]]] = Field(
        default=None,
        description="Prior conversation message turns [{'role': 'user'|'assistant', 'content': '...'}]",
    )


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
import json

logger = logging.getLogger(__name__)

from app.database.repositories.conversation_repo import ConversationRepository
from app.database.repositories.preference_repo import UserPreferenceRepository


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
    logger.info("Received user prompt: '%s' | existing state: %s | session: %s", req.message, req.state, req.session_id)
    try:
        conv_repo = ConversationRepository(db) if req.session_id else None
        pref_repo = UserPreferenceRepository(db)

        # 1. Resolve prior chat history (from explicit request or database session)
        history_msgs: Optional[List[ChatMessage]] = None
        if req.chat_history:
            history_msgs = [
                ChatMessage(role=m.get("role", "user"), content=m.get("content", ""))
                for m in req.chat_history
                if m.get("content")
            ]
        elif conv_repo and req.session_id:
            stored_msgs = conv_repo.get_recent_messages(req.session_id, limit=12)
            if stored_msgs:
                history_msgs = [
                    ChatMessage(role=m.role, content=m.content)
                    for m in stored_msgs
                    if m.role in ("user", "assistant")
                ]

        # 2. Resolve user preferences
        user_prefs = None
        user_id = req.user_id
        if not user_id and conv_repo and req.session_id:
            conv = conv_repo.get_or_create_conversation(req.session_id)
            user_id = conv.user_id

        if user_id:
            user_prefs = pref_repo.get_preferences_dict(user_id)

        # 3. Run Agent Orchestrator
        orchestrator = AgentOrchestrator(db=db, user_preferences=user_prefs)
        result = orchestrator.run(
            user_message=req.message,
            state=req.state,
            chat_history=history_msgs,
            user_preferences=user_prefs,
        )

        # 4. Persist messages to database if session_id provided
        if conv_repo and req.session_id:
            conv_repo.append_message(
                session_id=req.session_id,
                role="user",
                content=req.message,
                user_id=user_id,
            )
            for trace in result.tool_trace:
                conv_repo.append_message(
                    session_id=req.session_id,
                    role="tool",
                    content=json.dumps(trace.result),
                    tool_name=trace.tool_name,
                    tool_args=trace.arguments,
                    tool_result=trace.result,
                    user_id=user_id,
                )
            conv_repo.append_message(
                session_id=req.session_id,
                role="assistant",
                content=result.response,
                user_id=user_id,
            )

        logger.info(
            "Agent completed turn (tools executed: %d, response length: %d chars)",
            len(result.tool_trace),
            len(result.response),
        )
        return result
    except Exception as e:
        logger.error("Agent execution error for prompt '%s': %s", req.message, e, exc_info=True)
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Agent reasoning failed: {str(e)}",
        )
