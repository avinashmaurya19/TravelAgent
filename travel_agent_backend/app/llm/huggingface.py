"""Hugging Face Inference API LLM provider implementation."""

import json
import logging
from typing import List, Dict, Any, Optional
import httpx

from app.core.config import settings
from .base import LLMInterface, LLMResponse, ToolCall, ChatMessage

logger = logging.getLogger(__name__)


class HuggingFaceLLM(LLMInterface):
    """Hugging Face Inference provider for open-weights models."""

    BASE_URL = "https://api-inference.huggingface.co/models"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.api_key = api_key or settings.HUGGINGFACE_API_KEY
        self.model = model or settings.HUGGINGFACE_MODEL
        self.timeout = timeout
        self.is_placeholder_key = not self.api_key or self.api_key.startswith("hf_placeholder")

    def _mock_fallback(self, messages: List[ChatMessage], json_mode: bool = False) -> LLMResponse:
        """Deterministic mock fallback when using placeholder keys or offline."""
        last_message = next((m.content for m in reversed(messages) if m.role == "user"), "")
        if json_mode:
            return LLMResponse(
                content=json.dumps({
                    "intent": "SEARCH_FLIGHT",
                    "origin": "DEL",
                    "destination": "BOM",
                    "explanation": "HuggingFace fallback response",
                }),
                tool_calls=[],
                model=f"{self.model}-mock",
            )
        return LLMResponse(
            content=f"[Mock HF]: Response for: '{last_message}'. Provide HUGGINGFACE_API_KEY for live inference.",
            tool_calls=[],
            model=f"{self.model}-mock",
        )

    def generate_sync(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.1,
        max_tokens: int = 1000,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Synchronously generate text using Hugging Face router."""
        if self.is_placeholder_key:
            return self._mock_fallback(messages, json_mode=json_mode)

        url = f"{self.BASE_URL}/{self.model}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return LLMResponse(content=content, model=self.model)
        except Exception as e:
            logger.error("Hugging Face API error: %s. Using mock fallback.", e)
            return self._mock_fallback(messages, json_mode=json_mode)

    async def generate(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.1,
        max_tokens: int = 1000,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Asynchronously generate text using Hugging Face router."""
        if self.is_placeholder_key:
            return self._mock_fallback(messages, json_mode=json_mode)

        url = f"{self.BASE_URL}/{self.model}/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload, headers=headers)
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                return LLMResponse(content=content, model=self.model)
        except Exception as e:
            logger.error("Hugging Face API error: %s. Using mock fallback.", e)
            return self._mock_fallback(messages, json_mode=json_mode)

    def generate_with_tools_sync(
        self,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]],
        temperature: float = 0.1,
    ) -> LLMResponse:
        """Fallback tool generation for Hugging Face."""
        return self._mock_fallback(messages)

    async def generate_with_tools(
        self,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]],
        temperature: float = 0.1,
    ) -> LLMResponse:
        """Fallback tool generation for Hugging Face."""
        return self._mock_fallback(messages)
