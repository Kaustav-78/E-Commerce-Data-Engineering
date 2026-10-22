
from datetime import datetime


REQUIRED_FIELDS = {
    "event_id",
    "event_type",
    "event_time",
    "order_id",
    "customer_id",
    "product_id",
    "quantity",
    "unit_price",
}


def validate_event(event):
    """Validate an event against the expected schema."""

    if not isinstance(event, dict):
        raise ValueError("Event must be a JSON object")

    missing = REQUIRED_FIELDS - event.keys()

    if missing:
        raise ValueError(f"Missing fields: {sorted(missing)}")

    for field in (
        "event_id",
        "order_id",
        "customer_id",
        "product_id",
    ):
        if not isinstance(event[field], str) or not event[field].strip():
            raise ValueError(f"{field} must be a non-empty string")

    if event["event_type"] != "order_created":
        raise ValueError("Unsupported event_type")

    try:
        datetime.fromisoformat(
            event["event_time"].replace("Z", "+00:00")
        )
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Invalid event_time")

    quantity = event["quantity"]

    if (
        not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity <= 0
    ):
        raise ValueError("quantity must be a positive integer")

    price = event["unit_price"]

    if (
        not isinstance(price, (int, float))
        or isinstance(price, bool)
        or price <= 0
    ):
        raise ValueError("unit_price must be positive")

    return True
