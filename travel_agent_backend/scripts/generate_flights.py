"""Flight inventory mock data generator.

Generates 500+ realistic flights across major Indian routes with varied airlines,
prices, cabin classes, direct and layover flights spanning the next 30 days.
"""

import json
import random
import uuid
from datetime import datetime, date, timedelta, timezone
from pathlib import Path

from app.database.session import engine, SessionLocal, Base
from app.database.models import FlightModel

AIRLINES = [
    {"name": "IndiGo", "code": "6E", "has_biz": False},
    {"name": "Air India", "code": "AI", "has_biz": True},
    {"name": "Vistara", "code": "UK", "has_biz": True},
    {"name": "Akasa Air", "code": "QP", "has_biz": False},
    {"name": "SpiceJet", "code": "SG", "has_biz": False},
    {"name": "Emirates", "code": "EK", "has_biz": True},
]

ROUTES = [
    {"origin": "DEL", "dest": "BOM", "min_duration": 125, "base_price": 4200},
    {"origin": "BOM", "dest": "DEL", "min_duration": 130, "base_price": 4300},
    {"origin": "DEL", "dest": "BLR", "min_duration": 165, "base_price": 4800},
    {"origin": "BLR", "dest": "DEL", "min_duration": 170, "base_price": 4900},
    {"origin": "DEL", "dest": "GOI", "min_duration": 150, "base_price": 5400},
    {"origin": "GOI", "dest": "DEL", "min_duration": 155, "base_price": 5500},
    {"origin": "BOM", "dest": "GOI", "min_duration": 75, "base_price": 3200},
    {"origin": "GOI", "dest": "BOM", "min_duration": 80, "base_price": 3300},
    {"origin": "BLR", "dest": "GOI", "min_duration": 75, "base_price": 2900},
    {"origin": "GOI", "dest": "BLR", "min_duration": 80, "base_price": 3000},
    {"origin": "BOM", "dest": "BLR", "min_duration": 105, "base_price": 3800},
    {"origin": "BLR", "dest": "BOM", "min_duration": 105, "base_price": 3800},
    {"origin": "DEL", "dest": "CCU", "min_duration": 130, "base_price": 4500},
    {"origin": "CCU", "dest": "DEL", "min_duration": 135, "base_price": 4600},
    {"origin": "HYD", "dest": "DEL", "min_duration": 135, "base_price": 4400},
    {"origin": "DEL", "dest": "HYD", "min_duration": 130, "base_price": 4400},
    {"origin": "MAA", "dest": "DEL", "min_duration": 170, "base_price": 5100},
    {"origin": "DEL", "dest": "MAA", "min_duration": 165, "base_price": 5100},
    {"origin": "PNQ", "dest": "DEL", "min_duration": 130, "base_price": 4300},
    {"origin": "DEL", "dest": "PNQ", "min_duration": 125, "base_price": 4300},
    {"origin": "AMD", "dest": "BOM", "min_duration": 75, "base_price": 2800},
    {"origin": "BOM", "dest": "AMD", "min_duration": 70, "base_price": 2800},
    {"origin": "DEL", "dest": "DXB", "min_duration": 220, "base_price": 14500},
    {"origin": "DXB", "dest": "DEL", "min_duration": 215, "base_price": 14800},
    {"origin": "BOM", "dest": "DXB", "min_duration": 190, "base_price": 13200},
    {"origin": "DXB", "dest": "BOM", "min_duration": 195, "base_price": 13500},
]

DEPARTURE_SLOTS = [
    (6, 0), (7, 30), (8, 45), (10, 15), (11, 30),
    (13, 0), (14, 45), (16, 20), (18, 0), (19, 30),
    (21, 15), (22, 45),
]


def generate_flight_records(total_days: int = 30) -> list[FlightModel]:
    """Generate 500+ realistic flights over upcoming days."""
    random.seed(42)  # Deterministic seed for reproducible testing
    start_date = date.today()
    flights = []

    for day_offset in range(total_days):
        current_date = start_date + timedelta(days=day_offset)

        for route in ROUTES:
            # Generate 2 to 4 flights per route per day
            num_flights = random.randint(2, 4)
            chosen_slots = random.sample(DEPARTURE_SLOTS, num_flights)

            for hour, minute in chosen_slots:
                airline = random.choice(AIRLINES)
                flight_no = f"{airline['code']}-{random.randint(100, 999)}"

                # Decide if direct or 1-stop
                is_direct = random.random() < 0.75
                stops = 0 if is_direct else 1
                stops_details = None

                duration = route["min_duration"]
                if not is_direct:
                    layover_city = random.choice(["HYD", "AMD", "PNQ", "BOM", "DEL"])
                    if layover_city not in [route["origin"], route["dest"]]:
                        stops_details = [{"stop": layover_city, "layover_minutes": random.randint(45, 120)}]
                        duration += random.randint(60, 150)
                    else:
                        stops = 0

                dep_time = datetime(current_date.year, current_date.month, current_date.day, hour, minute)
                arr_time = dep_time + timedelta(minutes=duration)

                # Base pricing with realistic noise & time-of-day multiplier
                multiplier = 1.0
                if hour in [8, 9, 18, 19]:  # Peak business hours
                    multiplier = 1.25
                elif hour >= 21:  # Late night discount
                    multiplier = 0.88

                base_price = round(route["base_price"] * multiplier + random.randint(-400, 800), -1)

                # Economy flight
                flights.append(
                    FlightModel(
                        id=str(uuid.uuid4()),
                        flight_number=flight_no,
                        airline=airline["name"],
                        origin=route["origin"],
                        destination=route["dest"],
                        departure_time=dep_time,
                        arrival_time=arr_time,
                        duration_minutes=duration,
                        stops=stops,
                        stops_details=stops_details,
                        cabin_class="economy",
                        price=float(base_price),
                        available_seats=random.randint(15, 120),
                    )
                )

                # Add Business Class option for full-service airlines
                if airline["has_biz"] and random.random() < 0.6:
                    biz_price = round(base_price * 2.8, -2)
                    flights.append(
                        FlightModel(
                            id=str(uuid.uuid4()),
                            flight_number=f"{flight_no}-B",
                            airline=airline["name"],
                            origin=route["origin"],
                            destination=route["dest"],
                            departure_time=dep_time,
                            arrival_time=arr_time,
                            duration_minutes=duration,
                            stops=stops,
                            stops_details=stops_details,
                            cabin_class="business",
                            price=float(biz_price),
                            available_seats=random.randint(4, 20),
                        )
                    )

    return flights


def seed_database():
    """Create DB tables and insert generated flights."""
    print("Creating database schema...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        existing_count = db.query(FlightModel).count()
        if existing_count > 0:
            print(f"Database already contains {existing_count} flight records. Clearing existing records...")
            db.query(FlightModel).delete()
            db.commit()

        print("Generating mock flight inventory (30 days)...")
        flights = generate_flight_records(total_days=30)
        print(f"Generated {len(flights)} flight records. Seeding database...")

        db.bulk_save_objects(flights)
        db.commit()
        print(f"✅ Successfully seeded {len(flights)} flights into database!")

        # Also save JSON snapshot for inspection
        data_dir = Path(__file__).resolve().parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        json_path = data_dir / "flights.json"

        flights_json = [
            {
                "id": f.id,
                "flight_number": f.flight_number,
                "airline": f.airline,
                "origin": f.origin,
                "destination": f.destination,
                "departure_time": f.departure_time.isoformat(),
                "arrival_time": f.arrival_time.isoformat(),
                "duration_minutes": f.duration_minutes,
                "stops": f.stops,
                "cabin_class": f.cabin_class,
                "price": f.price,
                "available_seats": f.available_seats,
            }
            for f in flights[:50]  # Store first 50 as preview
        ]
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(flights_json, f, indent=2)
        print(f"📄 Saved sample JSON snapshot to {json_path}")

    finally:
        db.close()


def seed_if_empty():
    """Seed database with mock flights only if the table is currently empty."""
    db = SessionLocal()
    try:
        if db.query(FlightModel).count() == 0:
            print("Flight database is empty. Auto-seeding initial flight inventory...")
            flights = generate_flight_records(total_days=30)
            db.bulk_save_objects(flights)
            db.commit()
            print(f"✅ Successfully auto-seeded {len(flights)} flights!")
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
