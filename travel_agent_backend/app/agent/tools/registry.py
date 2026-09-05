"""Tool registry, schema specifications, and execution dispatcher."""

import logging
from typing import Dict, Any, List, Callable
from sqlalchemy.orm import Session

from .flight_search import search_flights_tool
from .flight_details import get_flight_details_tool
from .filtering import filter_flights_tool
from .availability import check_availability_tool
from .fare import calculate_fare_tool
from .booking import create_booking_tool

logger = logging.getLogger(__name__)

# Registered tool execution functions (Whitelist)
AVAILABLE_TOOLS: Dict[str, Callable[[Session, Dict[str, Any]], Dict[str, Any]]] = {
    "search_flights": search_flights_tool,
    "get_flight_details": get_flight_details_tool,
    "filter_flights": filter_flights_tool,
    "check_availability": check_availability_tool,
    "calculate_fare": calculate_fare_tool,
    "create_booking": create_booking_tool,
}

# OpenAI/Mistral Function Calling Tool Schemas
TOOL_SCHEMAS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "search_flights",
            "description": "Search for flights between an origin and destination on a given date.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {
                        "type": "string",
                        "description": "3-letter origin airport IATA code (e.g. DEL, BOM)",
                    },
                    "destination": {
                        "type": "string",
                        "description": "3-letter destination airport IATA code (e.g. BOM, BLR, GOI)",
                    },
                    "departure_date": {
                        "type": "string",
                        "description": "Departure date in YYYY-MM-DD format or 'tomorrow'",
                    },
                    "passengers": {
                        "type": "integer",
                        "description": "Number of passengers (1-9)",
                        "default": 1,
                    },
                    "cabin_class": {
                        "type": "string",
                        "enum": ["economy", "premium_economy", "business"],
                        "default": "economy",
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum budget ceiling in INR per ticket",
                    },
                    "max_stops": {
                        "type": "integer",
                        "description": "Maximum stops allowed (0 for non-stop)",
                    },
                    "preferred_airline": {
                        "type": "string",
                        "description": "Airline name filter, e.g. IndiGo, Air India",
                    },
                },
                "required": ["origin", "destination"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_flight_details",
            "description": "Retrieve comprehensive details for a specific flight by UUID or flight number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "flight_id": {
                        "type": "string",
                        "description": "Unique flight UUID or airline flight code (e.g. AI-559, 6E-204)",
                    },
                },
                "required": ["flight_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "filter_flights",
            "description": "Filter and refine search results by price limit, direct/non-stop, or airline.",
            "parameters": {
                "type": "object",
                "properties": {
                    "origin": {"type": "string", "description": "3-letter origin code"},
                    "destination": {"type": "string", "description": "3-letter destination code"},
                    "departure_date": {"type": "string", "description": "Departure date"},
                    "max_price": {"type": "number", "description": "Maximum price in INR"},
                    "max_stops": {"type": "integer", "description": "Max layovers (0 for direct)"},
                    "preferred_airline": {"type": "string", "description": "Airline filter"},
                    "sort_by": {
                        "type": "string",
                        "enum": ["price_asc", "price_desc", "duration_asc"],
                        "default": "price_asc",
                    },
                },
                "required": ["origin", "destination"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check real-time seat availability for a flight before booking.",
            "parameters": {
                "type": "object",
                "properties": {
                    "flight_id": {"type": "string", "description": "Flight UUID or flight code"},
                    "passengers": {"type": "integer", "default": 1, "description": "Number of seats"},
                },
                "required": ["flight_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_fare",
            "description": "Calculate itemized transparent fare breakdown including base fare, 18% GST, baggage, and seat selection fees.",
            "parameters": {
                "type": "object",
                "properties": {
                    "flight_id": {"type": "string", "description": "Flight UUID or flight code"},
                    "passengers": {"type": "integer", "default": 1},
                    "add_extra_baggage": {"type": "boolean", "default": False},
                    "seat_selection": {
                        "type": "string",
                        "enum": ["standard", "extra_legroom", "premium"],
                        "default": "standard",
                    },
                },
                "required": ["flight_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_booking",
            "description": "Initiate a pending flight reservation for passengers. Always requires explicit human confirmation before ticket issuance.",
            "parameters": {
                "type": "object",
                "properties": {
                    "flight_id": {"type": "string", "description": "Flight UUID or flight code"},
                    "passengers": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "first_name": {"type": "string"},
                                "last_name": {"type": "string"},
                                "age": {"type": "integer"},
                                "gender": {"type": "string"},
                                "seat_number": {"type": "string"},
                            },
                            "required": ["first_name", "last_name", "age", "gender"],
                        },
                    },
                    "add_extra_baggage": {"type": "boolean", "default": False},
                    "seat_selection": {"type": "string", "default": "standard"},
                    "contact_email": {"type": "string"},
                    "contact_phone": {"type": "string"},
                },
                "required": ["flight_id", "passengers"],
            },
        },
    },
]


def execute_tool(tool_name: str, arguments: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """Execute a registered tool with strict whitelist validation and exception containment."""
    if tool_name not in AVAILABLE_TOOLS:
        logger.error("Attempted invocation of unregistered tool: '%s'", tool_name)
        return {
            "status": "error",
            "error_type": "SecurityViolation",
            "message": f"Tool '{tool_name}' is not in the authorized tools whitelist.",
        }

    tool_fn = AVAILABLE_TOOLS[tool_name]
    try:
        result = tool_fn(db, arguments)
        return result
    except Exception as e:
        logger.exception("Error during execution of tool '%s': %s", tool_name, e)
        return {
            "status": "error",
            "error_type": type(e).__name__,
            "message": f"Failed to execute '{tool_name}': {str(e)}",
        }
