
from app.db import insert_event


class FakeCursor:
    """Simulate the minimum cursor behavior needed for this unit test."""

    def __init__(self, inserted=True):
        self.inserted = inserted
        self.query = None
        self.parameters = None

    def execute(self, query, parameters):
        self.query = query
        self.parameters = parameters

    def fetchone(self):
        return ("event-123",) if self.inserted else None


def test_insert_event_returns_true_for_new_event():
    cursor = FakeCursor(inserted=True)
    event = {"event_id": "event-123"}

    result = insert_event(cursor, event)

    assert result is True
    assert "ON CONFLICT (event_id) DO NOTHING" in cursor.query
    assert cursor.parameters is event


def test_insert_event_returns_false_for_duplicate():
    cursor = FakeCursor(inserted=False)
    event = {"event_id": "event-123"}

    result = insert_event(cursor, event)

    assert result is False
