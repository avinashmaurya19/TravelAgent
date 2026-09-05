"""Conversation repository for short-term chat memory and session persistence."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session

from app.database.models import ConversationModel, MessageModel


class ConversationRepository:
    """Data access methods for conversations and message history."""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_conversation(
        self,
        session_id: str,
        user_id: Optional[str] = None,
    ) -> ConversationModel:
        """Fetch existing conversation session or create a new one."""
        conversation = (
            self.db.query(ConversationModel)
            .filter(ConversationModel.session_id == session_id)
            .first()
        )
        if not conversation:
            conversation = ConversationModel(
                session_id=session_id,
                user_id=user_id,
                created_at=datetime.now(timezone.utc),
            )
            self.db.add(conversation)
            self.db.commit()
            self.db.refresh(conversation)
        elif user_id and not conversation.user_id:
            conversation.user_id = user_id
            self.db.commit()
            self.db.refresh(conversation)

        return conversation

    def append_message(
        self,
        session_id: str,
        role: str,
        content: str,
        tool_name: Optional[str] = None,
        tool_args: Optional[Dict[str, Any]] = None,
        tool_result: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
    ) -> MessageModel:
        """Append a user, assistant, or tool message to the conversation."""
        conversation = self.get_or_create_conversation(session_id, user_id=user_id)
        msg = MessageModel(
            conversation_id=conversation.id,
            role=role,
            content=content,
            tool_name=tool_name,
            tool_args=tool_args,
            tool_result=tool_result,
            timestamp=datetime.now(timezone.utc),
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_recent_messages(
        self,
        session_id: str,
        limit: int = 20,
    ) -> List[MessageModel]:
        """Fetch chronological message history for a conversation session."""
        conversation = (
            self.db.query(ConversationModel)
            .filter(ConversationModel.session_id == session_id)
            .first()
        )
        if not conversation:
            return []

        return (
            self.db.query(MessageModel)
            .filter(MessageModel.conversation_id == conversation.id)
            .order_by(MessageModel.timestamp.asc())
            .limit(limit)
            .all()
        )

    def clear_conversation(self, session_id: str) -> bool:
        """Delete conversation and its associated messages."""
        conversation = (
            self.db.query(ConversationModel)
            .filter(ConversationModel.session_id == session_id)
            .first()
        )
        if conversation:
            self.db.delete(conversation)
            self.db.commit()
            return True
        return False
