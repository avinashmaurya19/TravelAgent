"""Unit tests for LLM provider abstraction and Mistral integration."""

import pytest
from app.llm.base import ChatMessage, ToolCall, LLMResponse
from app.llm.mistral import MistralLLM
from app.llm.huggingface import HuggingFaceLLM


def test_chat_message_to_dict():
    """Verify ChatMessage converts properly to API dictionary format."""
    msg = ChatMessage(role="user", content="Hello world")
    data = msg.to_dict()
    assert data == {"role": "user", "content": "Hello world"}

    tool_msg = ChatMessage(role="tool", content="{'flights': []}", tool_call_id="call_123")
    assert tool_msg.to_dict()["tool_call_id"] == "call_123"


def test_llm_response_structure():
    """Verify LLMResponse structure with tool calls."""
    tc = ToolCall(id="call_1", name="search_flights", arguments={"origin": "DEL"})
    resp = LLMResponse(content=None, tool_calls=[tc], model="mistral-small-latest")
    assert len(resp.tool_calls) == 1
    assert resp.tool_calls[0].name == "search_flights"
    assert resp.tool_calls[0].arguments["origin"] == "DEL"


def test_mistral_mock_fallback_json_mode():
    """Verify MistralLLM offline fallback outputs valid JSON intent when using placeholder key."""
    llm = MistralLLM(api_key="random_mistral_api_key_placeholder")
    messages = [
        ChatMessage(role="system", content="Extract intent"),
        ChatMessage(role="user", content="Flights from Delhi to Bangalore under 6000"),
    ]
    resp = llm.generate_sync(messages=messages, json_mode=True)
    assert resp.content is not None
    import json
    parsed = json.loads(resp.content)
    assert parsed["intent"] == "SEARCH_FLIGHT"
    assert parsed["origin"] == "DEL"
    assert parsed["destination"] == "BLR"
    assert parsed["max_price"] == 6000.0


@pytest.mark.asyncio
async def test_mistral_async_mock_fallback():
    """Verify async MistralLLM generation works."""
    llm = MistralLLM(api_key="random_placeholder")
    messages = [ChatMessage(role="user", content="Show me baggage policy")]
    resp = await llm.generate(messages=messages, json_mode=True)
    assert resp.content is not None
    import json
    data = json.loads(resp.content)
    assert data["intent"] == "TRAVEL_POLICY"


def test_huggingface_mock_fallback():
    """Verify HuggingFaceLLM fallback when API key is missing/placeholder."""
    llm = HuggingFaceLLM(api_key=None)
    messages = [ChatMessage(role="user", content="Flights to Goa")]
    resp = llm.generate_sync(messages=messages)
    assert resp.content is not None
    assert "Mock HF" in resp.content
