"""SQLAlchemy ORM models for TravelAgent AI."""

import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    DateTime,
    ForeignKey,
    Text,
    JSON,
    Enum as SQLEnum,
)
from sqlalchemy.orm import relationship
import enum

from app.database.session import Base


class BookingStatus(str, enum.Enum):
    """Booking lifecycle status."""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"


class CabinClass(str, enum.Enum):
    """Cabin class types."""
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class UserModel(Base):
    """User account model."""
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    preferences = relationship("UserPreferenceModel", back_populates="user", uselist=False, cascade="all, delete-orphan")
    bookings = relationship("BookingModel", back_populates="user")
    conversations = relationship("ConversationModel", back_populates="user")


class UserPreferenceModel(Base):
    """User long-term travel preferences."""
    __tablename__ = "user_preferences"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    preferred_cabin = Column(String(50), default="economy", nullable=False)
    preferred_airline = Column(String(100), nullable=True)
    max_stops = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("UserModel", back_populates="preferences")


class FlightModel(Base):
    """Flight inventory model."""
    __tablename__ = "flights"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    flight_number = Column(String(20), nullable=False, index=True)
    airline = Column(String(100), nullable=False, index=True)
    origin = Column(String(10), nullable=False, index=True)  # Airport code e.g. DEL
    destination = Column(String(10), nullable=False, index=True)  # Airport code e.g. BOM
    departure_time = Column(DateTime, nullable=False, index=True)
    arrival_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    stops = Column(Integer, default=0, nullable=False)
    stops_details = Column(JSON, nullable=True)  # List of layover airport codes or notes
    cabin_class = Column(String(50), default="economy", nullable=False)
    price = Column(Float, nullable=False)  # Base price in INR
    available_seats = Column(Integer, default=100, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    bookings = relationship("BookingModel", back_populates="flight")


class BookingModel(Base):
    """Flight booking record."""
    __tablename__ = "bookings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_reference = Column(String(12), unique=True, nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    flight_id = Column(String(36), ForeignKey("flights.id"), nullable=False)
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.PENDING, nullable=False)
    
    # Fare breakdown
    base_fare = Column(Float, nullable=False)
    tax_amount = Column(Float, nullable=False)
    baggage_fee = Column(Float, default=0.0, nullable=False)
    seat_fee = Column(Float, default=0.0, nullable=False)
    total_price = Column(Float, nullable=False)
    
    passengers_count = Column(Integer, default=1, nullable=False)
    contact_email = Column(String(255), nullable=True)
    contact_phone = Column(String(50), nullable=True)
    
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    confirmed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)

    user = relationship("UserModel", back_populates="bookings")
    flight = relationship("FlightModel", back_populates="bookings")
    passengers = relationship("PassengerModel", back_populates="booking", cascade="all, delete-orphan")


class PassengerModel(Base):
    """Individual passenger on a booking."""
    __tablename__ = "passengers"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    booking_id = Column(String(36), ForeignKey("bookings.id", ondelete="CASCADE"), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False)
    seat_number = Column(String(10), nullable=True)

    booking = relationship("BookingModel", back_populates="passengers")


class ConversationModel(Base):
    """Conversation session for short-term chat memory."""
    __tablename__ = "conversations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    user = relationship("UserModel", back_populates="conversations")
    messages = relationship("MessageModel", back_populates="conversation", cascade="all, delete-orphan")


class MessageModel(Base):
    """Individual message within a conversation."""
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey("conversations.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user', 'assistant', 'system', 'tool'
    content = Column(Text, nullable=False)
    tool_name = Column(String(100), nullable=True)
    tool_args = Column(JSON, nullable=True)
    tool_result = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    conversation = relationship("ConversationModel", back_populates="messages")
