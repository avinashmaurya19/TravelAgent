"""Pytest fixtures and test database setup."""

import pytest
from datetime import datetime, date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.session import Base, get_db
from app.database.models import FlightModel
from app.main import app

# In-memory SQLite for fast, isolated unit testing
TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Create fresh database tables for each test function."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        # Seed test flight data
        today = date.today()
        test_flights = [
            FlightModel(
                id="flight-del-bom-1",
                flight_number="6E-204",
                airline="IndiGo",
                origin="DEL",
                destination="BOM",
                departure_time=datetime(today.year, today.month, today.day, 8, 30),
                arrival_time=datetime(today.year, today.month, today.day, 10, 45),
                duration_minutes=135,
                stops=0,
                cabin_class="economy",
                price=4500.0,
                available_seats=50,
            ),
            FlightModel(
                id="flight-del-bom-2",
                flight_number="AI-802",
                airline="Air India",
                origin="DEL",
                destination="BOM",
                departure_time=datetime(today.year, today.month, today.day, 14, 0),
                arrival_time=datetime(today.year, today.month, today.day, 16, 15),
                duration_minutes=135,
                stops=0,
                cabin_class="economy",
                price=5200.0,
                available_seats=20,
            ),
            FlightModel(
                id="flight-del-bom-biz",
                flight_number="AI-802-B",
                airline="Air India",
                origin="DEL",
                destination="BOM",
                departure_time=datetime(today.year, today.month, today.day, 14, 0),
                arrival_time=datetime(today.year, today.month, today.day, 16, 15),
                duration_minutes=135,
                stops=0,
                cabin_class="business",
                price=14000.0,
                available_seats=8,
            ),
            FlightModel(
                id="flight-del-goi-1",
                flight_number="UK-845",
                airline="Vistara",
                origin="DEL",
                destination="GOI",
                departure_time=datetime(today.year, today.month, today.day, 11, 0),
                arrival_time=datetime(today.year, today.month, today.day, 13, 30),
                duration_minutes=150,
                stops=0,
                cabin_class="economy",
                price=6200.0,
                available_seats=30,
            ),
            FlightModel(
                id="flight-del-bom-lowseats",
                flight_number="SG-101",
                airline="SpiceJet",
                origin="DEL",
                destination="BOM",
                departure_time=datetime(today.year, today.month, today.day, 19, 0),
                arrival_time=datetime(today.year, today.month, today.day, 21, 15),
                duration_minutes=135,
                stops=0,
                cabin_class="economy",
                price=3800.0,
                available_seats=2,
            ),
        ]
        session.bulk_save_objects(test_flights)
        session.commit()
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """FastAPI TestClient with overridden database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
