"""User preference repository for long-term travel preferences."""

from datetime import datetime, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.database.models import UserModel, UserPreferenceModel


class UserPreferenceRepository:
    """Data access methods for user profiles and travel preferences."""

    def __init__(self, db: Session):
        self.db = db

    def get_or_create_user(self, name: str, email: str) -> UserModel:
        """Fetch existing user by email or create a new user profile."""
        user = self.db.query(UserModel).filter(UserModel.email == email.lower()).first()
        if not user:
            user = UserModel(
                name=name,
                email=email.lower(),
                created_at=datetime.now(timezone.utc),
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        return user

    def get_user_by_id(self, user_id: str) -> Optional[UserModel]:
        """Fetch user by primary UUID."""
        return self.db.query(UserModel).filter(UserModel.id == user_id).first()

    def get_preferences(self, user_id: str) -> Optional[UserPreferenceModel]:
        """Retrieve stored travel preferences for a user."""
        return (
            self.db.query(UserPreferenceModel)
            .filter(UserPreferenceModel.user_id == user_id)
            .first()
        )

    def set_preferences(
        self,
        user_id: str,
        preferred_cabin: str = "economy",
        preferred_airline: Optional[str] = None,
        max_stops: Optional[int] = None,
    ) -> UserPreferenceModel:
        """Upsert travel preferences for a user."""
        prefs = self.get_preferences(user_id)
        if not prefs:
            prefs = UserPreferenceModel(
                user_id=user_id,
                preferred_cabin=preferred_cabin,
                preferred_airline=preferred_airline,
                max_stops=max_stops,
                created_at=datetime.now(timezone.utc),
            )
            self.db.add(prefs)
        else:
            prefs.preferred_cabin = preferred_cabin
            prefs.preferred_airline = preferred_airline
            prefs.max_stops = max_stops

        self.db.commit()
        self.db.refresh(prefs)
        return prefs

    def get_preferences_dict(self, user_id: Optional[str]) -> Optional[Dict[str, Any]]:
        """Return user preferences as dictionary for ranking injection."""
        if not user_id:
            return None
        prefs = self.get_preferences(user_id)
        if not prefs:
            return None
        return {
            "preferred_cabin": prefs.preferred_cabin,
            "preferred_airline": prefs.preferred_airline,
            "max_stops": prefs.max_stops,
        }
