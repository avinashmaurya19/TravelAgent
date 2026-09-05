"""Mistral AI LLM provider implementation."""

import json
import logging
from typing import List, Dict, Any, Optional
import httpx

from app.core.config import settings
from .base import LLMInterface, LLMResponse, ToolCall, ChatMessage

logger = logging.getLogger(__name__)


class MistralLLM(LLMInterface):
    """Mistral AI API client implementation with structured output and tool calling."""

    API_URL = "https://api.mistral.ai/v1/chat/completions"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.api_key = api_key or settings.MISTRAL_API_KEY
        self.model = model or settings.MISTRAL_MODEL
        self.timeout = timeout
        self.is_placeholder_key = (
            not self.api_key
            or self.api_key.startswith("random_")
            or self.api_key.startswith("mock_")
            or self.api_key == "random_mistral_api_key_placeholder"
        )

    def _build_payload(
        self,
        messages: List[ChatMessage],
        temperature: float,
        max_tokens: int,
        json_mode: bool = False,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Build request payload for Mistral AI chat completions endpoint."""
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [m.to_dict() for m in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        return payload

    def _parse_response(self, data: Dict[str, Any]) -> LLMResponse:
        """Parse raw Mistral API response JSON into standard LLMResponse."""
        choice = data["choices"][0]
        message_data = choice["message"]
        content = message_data.get("content")

        tool_calls: List[ToolCall] = []
        if "tool_calls" in message_data and message_data["tool_calls"]:
            for tc in message_data["tool_calls"]:
                func = tc.get("function", {})
                args = func.get("arguments", "{}")
                if isinstance(args, str):
                    try:
                        parsed_args = json.loads(args)
                    except json.JSONDecodeError:
                        parsed_args = {"raw": args}
                else:
                    parsed_args = args

                tool_calls.append(
                    ToolCall(
                        id=tc.get("id", "call_default"),
                        name=func.get("name", "unknown_tool"),
                        arguments=parsed_args,
                    )
                )

        usage = data.get("usage")
        return LLMResponse(
            content=content,
            tool_calls=tool_calls,
            model=data.get("model", self.model),
            usage=usage,
        )

    def _mock_fallback(
        self,
        messages: List[ChatMessage],
        json_mode: bool = False,
        tools: Optional[List[Dict[str, Any]]] = None,
    ) -> LLMResponse:
        """Deterministic mock fallback when using placeholder keys or in offline mode."""
        last_message = next((m.content for m in reversed(messages) if m.role == "user"), "")
        lower = last_message.lower()

        if json_mode:
            # Generate deterministic structured intent JSON based on user text
            intent_data = self._mock_intent_json(lower)
            return LLMResponse(
                content=json.dumps(intent_data),
                tool_calls=[],
                model=f"{self.model}-mock",
            )

        if tools and ("flight" in lower or "search" in lower or "del" in lower):
            # Generate mock search_flights tool call
            return LLMResponse(
                content=None,
                tool_calls=[
                    ToolCall(
                        id="call_mock_search_1",
                        name="search_flights",
                        arguments={
                            "origin": "DEL",
                            "destination": "BOM",
                            "passengers": 1,
                        },
                    )
                ],
                model=f"{self.model}-mock",
            )

        return LLMResponse(
            content=f"[Mock Mistral]: I received your message: '{last_message}'. Set a live MISTRAL_API_KEY for live responses.",
            tool_calls=[],
            model=f"{self.model}-mock",
        )

    def _mock_intent_json(self, lower: str) -> Dict[str, Any]:
        """Extract deterministic intent attributes from natural text for offline mock mode."""
        intent = "SEARCH_FLIGHT"
        origin = None
        destination = None
        max_price = None
        max_stops = None
        airline = None
        booking_ref = None
        policy_topic = None

        if "cancel" in lower:
            intent = "CANCEL_BOOKING"
        elif "check" in lower or "status" in lower or "pnr" in lower or "lookup" in lower:
            intent = "CHECK_BOOKING"
            import re
            pnr_match = re.search(r'(?:booking|pnr|reference|ticket)\s*(?:for|of|is|#|id)?\s*([A-Z0-9\-]{5,15})', lower.upper())
            if pnr_match:
                booking_ref = pnr_match.group(1).strip("-")
            else:
                pnr_match = re.search(r'\b([A-Z]{3,}[0-9]+[A-Z0-9]*|[0-9]+[A-Z]+[A-Z0-9]*)\b', lower.upper())
                if pnr_match:
                    booking_ref = pnr_match.group(0)
        elif "baggage" in lower or "refund" in lower or "policy" in lower:
            intent = "TRAVEL_POLICY"
            policy_topic = "baggage" if "baggage" in lower else "refund"
        elif "compare" in lower:
            intent = "COMPARE_FLIGHTS"
        elif "book" in lower or "reserve" in lower:
            intent = "BOOK_FLIGHT"
        else:
            intent = "SEARCH_FLIGHT"

        # City & route extraction
        city_map = {
            "delhi": "DEL", "del": "DEL",
            "mumbai": "BOM", "bom": "BOM",
            "bangalore": "BLR", "blr": "BLR", "bengaluru": "BLR",
            "goa": "GOI", "goi": "GOI",
            "kolkata": "CCU", "ccu": "CCU",
            "hyderabad": "HYD", "hyd": "HYD",
            "chennai": "MAA", "maa": "MAA",
        }

        import re
        route_match = re.search(r'from\s+([a-zA-Z]+)\s+to\s+([a-zA-Z]+)', lower)
        if route_match:
            o_cand = route_match.group(1).lower()
            d_cand = route_match.group(2).lower()
            origin = city_map.get(o_cand, o_cand[:3].upper())
            destination = city_map.get(d_cand, d_cand[:3].upper())
        else:
            # Check cities mentioned
            found_cities = []
            for city_name, code in city_map.items():
                pos = lower.find(city_name)
                if pos != -1:
                    found_cities.append((pos, code))
            found_cities.sort(key=lambda x: x[0])
            if len(found_cities) >= 2:
                origin = found_cities[0][1]
                destination = found_cities[1][1]
            elif len(found_cities) == 1:
                origin = found_cities[0][1]

        if "non-stop" in lower or "nonstop" in lower or "direct" in lower:
            max_stops = 0

        if "indigo" in lower:
            airline = "IndiGo"
        elif "air india" in lower:
            airline = "Air India"
        elif "spicejet" in lower:
            airline = "SpiceJet"

        price_match = re.search(r'(?:under|below|budget|max|₹)\s*(\d+[\d,]*)', lower)
        if price_match:
            max_price = float(price_match.group(1).replace(",", ""))

        return {
            "intent": intent,
            "origin": origin,
            "destination": destination,
            "date": "tomorrow" if "tomorrow" in lower else None,
            "passengers": 1,
            "cabin_class": "economy",
            "max_price": max_price,
            "max_stops": max_stops,
            "preferred_airline": airline,
            "booking_reference": booking_ref,
            "policy_topic": policy_topic,
            "explanation": f"Recognized intent {intent} from user query.",
        }

    def generate_sync(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.1,
        max_tokens: int = 1000,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Synchronously generate completions via Mistral AI."""
        if self.is_placeholder_key:
            return self._mock_fallback(messages, json_mode=json_mode)

        payload = self._build_payload(messages, temperature, max_tokens, json_mode=json_mode)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(self.API_URL, json=payload, headers=headers)
                if resp.status_code == 401:
                    logger.warning("Mistral API key returned 401 Unauthorized. Using mock fallback.")
                    return self._mock_fallback(messages, json_mode=json_mode)
                resp.raise_for_status()
                return self._parse_response(resp.json())
        except Exception as e:
            logger.error("Mistral API error: %s. Falling back to mock.", e)
            return self._mock_fallback(messages, json_mode=json_mode)

    async def generate(
        self,
        messages: List[ChatMessage],
        temperature: float = 0.1,
        max_tokens: int = 1000,
        json_mode: bool = False,
    ) -> LLMResponse:
        """Asynchronously generate completions via Mistral AI."""
        if self.is_placeholder_key:
            return self._mock_fallback(messages, json_mode=json_mode)

        payload = self._build_payload(messages, temperature, max_tokens, json_mode=json_mode)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(self.API_URL, json=payload, headers=headers)
                if resp.status_code == 401:
                    logger.warning("Mistral API key returned 401 Unauthorized. Using mock fallback.")
                    return self._mock_fallback(messages, json_mode=json_mode)
                resp.raise_for_status()
                return self._parse_response(resp.json())
        except Exception as e:
            logger.error("Mistral API error: %s. Falling back to mock.", e)
            return self._mock_fallback(messages, json_mode=json_mode)

    def generate_with_tools_sync(
        self,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]],
        temperature: float = 0.1,
    ) -> LLMResponse:
        """Synchronously generate tool calls via Mistral AI."""
        if self.is_placeholder_key:
            return self._mock_fallback(messages, tools=tools)

        payload = self._build_payload(messages, temperature, max_tokens=1000, tools=tools)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(self.API_URL, json=payload, headers=headers)
                if resp.status_code == 401:
                    return self._mock_fallback(messages, tools=tools)
                resp.raise_for_status()
                return self._parse_response(resp.json())
        except Exception as e:
            logger.error("Mistral tool call error: %s. Using mock fallback.", e)
            return self._mock_fallback(messages, tools=tools)

    async def generate_with_tools(
        self,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]],
        temperature: float = 0.1,
    ) -> LLMResponse:
        """Asynchronously generate tool calls via Mistral AI."""
        if self.is_placeholder_key:
            return self._mock_fallback(messages, tools=tools)

        payload = self._build_payload(messages, temperature, max_tokens=1000, tools=tools)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(self.API_URL, json=payload, headers=headers)
                if resp.status_code == 401:
                    return self._mock_fallback(messages, tools=tools)
                resp.raise_for_status()
                return self._parse_response(resp.json())
        except Exception as e:
            logger.error("Mistral tool call error: %s. Using mock fallback.", e)
            return self._mock_fallback(messages, tools=tools)
