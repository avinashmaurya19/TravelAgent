"""Abstract base class and data models for LLM providers."""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Standard message representation for chat completions."""
    role: str = Field(..., description="Role: 'system', 'user', 'assistant', or 'tool'")
    content: str = Field(..., description="Text content of the message")
    name: Optional[str] = Field(default=None, description="Optional name identifier")
    tool_call_id: Optional[str] = Field(default=None, description="Tool call ID for tool outputs")
    tool_calls: Optional[List[Dict[str, Any]]] = Field(default=None, description="List of tool calls if emitted by assistant")

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for API serialization."""
        data: Dict[str, Any] = {"role": self.role, "content": self.content}
        if self.name:
            data["name"] = self.name
        if self.tool_call_id:
            data["tool_call_id"] = self.tool_call_id
        if self.tool_calls:
            data["tool_calls"] = self.tool_calls
        return data


class ToolCall(BaseModel):
    """Structured tool invocation emitted by the model."""
    id: str = Field(..., description="Unique tool call ID")
    name: str = Field(..., description="Tool/function name to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Parsed tool arguments")


class LLMResponse(BaseModel):
    """Standardized response from an LLM invocation."""
    content: Optional[str] = Field(default=None, description="Assistant natural language text response")
    tool_calls: List[ToolCall] = Field(default_factory=list, description="Emitted tool calls")
    model: str = Field(..., description="Model identifier used for generation")
    usage: Optional[Dict[str, Any]] = Field(default=None, description="Token usage statistics")


class LLMInterface(ABC):
    """Abstract interface defining required LLM capabilities."""

    @abstractmethod
    def generate_sync(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.1,
        max_tokens: int = 1000,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Synchronously generate text or structured JSON from chat messages."""
        pass

    @abstractmethod
    async def generate(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.1,
        max_tokens: int = 1000,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Asynchronously generate text or structured JSON from chat messages."""
        pass

    @abstractmethod
    def generate_with_tools_sync(
        self,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]],
        temperature: float = 0.1,
    ) -> LLMResponse:
        """Synchronously generate a completion with tool/function schemas."""
        pass

    @abstractmethod
    async def generate_with_tools(
        self,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]],
        temperature: float = 0.1,
    ) -> LLMResponse:
        """Asynchronously generate a completion with tool/function schemas."""
        pass
