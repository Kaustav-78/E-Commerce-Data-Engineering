
import pytest

from app.event_generator import generate_event
from app.validator import validate_event


def test_valid_event_passes():
    event = generate_event(1)
    assert validate_event(event) is True


def test_missing_field_is_rejected():
    event = generate_event(1)
    del event["order_id"]

    with pytest.raises(ValueError, match="Missing fields"):
        validate_event(event)


def test_negative_quantity_is_rejected():
    event = generate_event(1)
    event["quantity"] = -1

    with pytest.raises(ValueError, match="positive integer"):
        validate_event(event)


def test_zero_price_is_rejected():
    event = generate_event(1)
    event["unit_price"] = 0

    with pytest.raises(ValueError, match="unit_price"):
        validate_event(event)
