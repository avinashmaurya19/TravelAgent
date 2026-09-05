"""Structured intent recognition engine using LLM and Pydantic validation."""

import json
import re
import logging
from typing import Optional, List

from app.llm.base import LLMInterface, ChatMessage
from app.llm.mistral import MistralLLM
from .intents import AgentIntent, IntentType
from .prompts import INTENT_EXTRACTION_SYSTEM_PROMPT, FEW_SHOT_EXAMPLES

logger = logging.getLogger(__name__)


class IntentEngine:
    """Classifies user queries into structured AgentIntent schemas."""

    def __init__(self, llm: Optional[LLMInterface] = None):
        self.llm = llm or MistralLLM()

    def _build_messages(self, query: str, context: Optional[str] = None) -> List[ChatMessage]:
        """Construct prompt messages including system prompt, few-shot examples, and user query."""
        messages: List[ChatMessage] = [
            ChatMessage(role="system", content=INTENT_EXTRACTION_SYSTEM_PROMPT),
        ]

        # Add few-shot examples
        for eg in FEW_SHOT_EXAMPLES:
            messages.append(ChatMessage(role="user", content=eg["user"]))
            messages.append(ChatMessage(role="assistant", content=eg["assistant"]))

        # Include prior conversation context if available
        user_content = query
        if context:
            user_content = f"Context: {context}\nUser Request: {query}"

        messages.append(ChatMessage(role="user", content=user_content))
        return messages

    def _parse_and_validate_json(self, raw_content: str, query: str) -> AgentIntent:
        """Extract and validate JSON string into AgentIntent model."""
        content = raw_content.strip()

        # Strip markdown code fences if model wrapped response in ```json ... ```
        if "```" in content:
            match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", content)
            if match:
                content = match.group(1).strip()

        try:
            data = json.loads(content)
            return AgentIntent.model_validate(data)
        except Exception as e:
            logger.warning("Failed to parse LLM intent JSON: %s. Raw: %s", e, raw_content)
            # Safe fallback: classify as GENERAL_TRAVEL with raw query
            return AgentIntent(
                intent=IntentType.GENERAL_TRAVEL,
                explanation=f"Fallback due to parsing error: {e}",
            )

    def recognize_intent_sync(self, query: str, context: Optional[str] = None) -> AgentIntent:
        """Synchronously classify user query and extract structured parameters."""
        messages = self._build_messages(query, context)
        response = self.llm.generate_sync(messages=messages, temperature=0.1, json_mode=True)
        if not response.content:
            return AgentIntent(intent=IntentType.GENERAL_TRAVEL, explanation="Empty model response")
        return self._parse_and_validate_json(response.content, query)

    async def recognize_intent(self, query: str, context: Optional[str] = None) -> AgentIntent:
        """Asynchronously classify user query and extract structured parameters."""
        messages = self._build_messages(query, context)
        response = await self.llm.generate(messages=messages, temperature=0.1, json_mode=True)
        if not response.content:
            return AgentIntent(intent=IntentType.GENERAL_TRAVEL, explanation="Empty model response")
        return self._parse_and_validate_json(response.content, query)
