
from app.event_generator import generate_events


def test_event_generation_is_deterministic():
    first_run = generate_events(count=10, seed=42)
    second_run = generate_events(count=10, seed=42)

    assert first_run == second_run


def test_generator_adds_duplicate_and_invalid_records():
    events = generate_events(count=10, seed=42)

    assert len(events) == 12
    assert events[-2] == events[0]
    assert events[-1]["quantity"] == -5
