
import json
import random
import uuid
from datetime import datetime, timedelta, timezone

from app.config import RAW_FILE, create_directories


PRODUCTS = [
    ("P101", 499.00),
    ("P102", 799.00),
    ("P103", 1299.00),
    ("P104", 249.00),
    ("P105", 1999.00),
]

# Fixed namespace and timestamp make generated events repeatable.
EVENT_NAMESPACE = uuid.UUID("12345678-1234-5678-1234-567812345678")
BASE_EVENT_TIME = datetime(2026, 1, 1, tzinfo=timezone.utc)


def generate_event(index, rng=None):
    """Generate one repeatable simulated order event."""
    if rng is None:
        rng = random

    product_id, unit_price = rng.choice(PRODUCTS)

    event_time = BASE_EVENT_TIME - timedelta(
        seconds=rng.randint(0, 3600)
    )

    return {
        "event_id": str(
            uuid.uuid5(EVENT_NAMESPACE, f"order-{index}")
        ),
        "event_type": "order_created",
        "event_time": event_time.isoformat(),
        "order_id": f"ORD{index:06d}",
        "customer_id": f"CUST{rng.randint(1, 500):04d}",
        "product_id": product_id,
        "quantity": rng.randint(1, 5),
        "unit_price": unit_price,
    }


def generate_events(count=100, seed=42):
    """Generate repeatable events, including duplicate and invalid records."""
    rng = random.Random(seed)

    events = [
        generate_event(index, rng)
        for index in range(1, count + 1)
    ]

    if len(events) >= 2:
        # Simulate a duplicate delivery.
        events.append(events[0].copy())

        # Simulate invalid business data.
        invalid_event = events[1].copy()
        invalid_event["quantity"] = -5
        events.append(invalid_event)

    return events


def write_raw_events(events):
    """Write events as newline-delimited JSON."""
    create_directories()

    with RAW_FILE.open("w", encoding="utf-8") as file:
        for event in events:
            file.write(json.dumps(event) + "\n")
