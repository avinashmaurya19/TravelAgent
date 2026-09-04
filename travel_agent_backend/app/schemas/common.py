"""Common Pydantic schemas and standard response envelopes."""

from typing import Generic, TypeVar, Optional, Any
from pydantic import BaseModel, Field

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Generic API response envelope."""
    success: bool = Field(default=True, description="Indicates if the request succeeded")
    message: Optional[str] = Field(default=None, description="Descriptive status message")
    data: Optional[T] = Field(default=None, description="Payload data")
    error: Optional[Any] = Field(default=None, description="Error details if success is False")


class ErrorDetail(BaseModel):
    """Structured error detail schema."""
    code: str
    message: str
    details: Optional[Any] = None
