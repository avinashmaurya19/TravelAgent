"""API endpoints for user profile and travel preference management."""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.database.repositories.preference_repo import UserPreferenceRepository

router = APIRouter(prefix="/users", tags=["Users & Preferences"])


class UserCreateRequest(BaseModel):
    """Payload to create or retrieve user profile."""
    name: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., min_length=3, max_length=255)


class UserPreferencePayload(BaseModel):
    """User travel preference configuration."""
    preferred_cabin: str = Field(default="economy", description="economy, premium_economy, business, first")
    preferred_airline: Optional[str] = Field(default=None, description="Preferred airline name (e.g. IndiGo, Air India)")
    max_stops: Optional[int] = Field(default=None, description="Maximum stops preferred (e.g. 0 for non-stop)")


class UserResponse(BaseModel):
    """User profile response."""
    id: str
    name: str
    email: str


class UserPreferenceResponse(BaseModel):
    """User preference response."""
    user_id: str
    preferred_cabin: str
    preferred_airline: Optional[str]
    max_stops: Optional[int]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def get_or_create_user(
    req: UserCreateRequest,
    db: Session = Depends(get_db),
) -> UserResponse:
    """Create a new user or fetch existing user profile by email."""
    repo = UserPreferenceRepository(db)
    user = repo.get_or_create_user(name=req.name, email=req.email)
    return UserResponse(id=user.id, name=user.name, email=user.email)


@router.get("/{user_id}/preferences", response_model=UserPreferenceResponse)
def get_user_preferences(
    user_id: str,
    db: Session = Depends(get_db),
) -> UserPreferenceResponse:
    """Retrieve saved travel preferences for a user."""
    repo = UserPreferenceRepository(db)
    user = repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    prefs = repo.get_preferences(user_id)
    if not prefs:
        return UserPreferenceResponse(
            user_id=user_id,
            preferred_cabin="economy",
            preferred_airline=None,
            max_stops=None,
        )

    return UserPreferenceResponse(
        user_id=user_id,
        preferred_cabin=prefs.preferred_cabin,
        preferred_airline=prefs.preferred_airline,
        max_stops=prefs.max_stops,
    )


@router.put("/{user_id}/preferences", response_model=UserPreferenceResponse)
def update_user_preferences(
    user_id: str,
    payload: UserPreferencePayload,
    db: Session = Depends(get_db),
) -> UserPreferenceResponse:
    """Update or create travel preferences for a user."""
    repo = UserPreferenceRepository(db)
    user = repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    prefs = repo.set_preferences(
        user_id=user_id,
        preferred_cabin=payload.preferred_cabin,
        preferred_airline=payload.preferred_airline,
        max_stops=payload.max_stops,
    )
    return UserPreferenceResponse(
        user_id=user_id,
        preferred_cabin=prefs.preferred_cabin,
        preferred_airline=prefs.preferred_airline,
        max_stops=prefs.max_stops,
    )
