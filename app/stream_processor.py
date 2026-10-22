
import json
from datetime import datetime, timezone

from app.config import QUARANTINE_FILE, create_directories
from app.db import get_connection, insert_event
from app.logger import get_logger
from app.validator import validate_event

logger = get_logger(__name__)


def quarantine_event(event, error):
    """Persist an invalid event and its error details."""
    create_directories()

    record = {
        "quarantined_at": datetime.now(timezone.utc).isoformat(),
        "raw_record": event,
        "error": str(error),
    }

    with QUARANTINE_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(record, default=str) + "\n")

    logger.warning(
        "Kafka event quarantined: error=%s file=%s",
        error,
        QUARANTINE_FILE,
    )


def process_stream_event(event):
    """Validate and load one Kafka event into PostgreSQL."""

    try:
        validate_event(event)

    except (ValueError, KeyError, TypeError) as error:
        quarantine_event(event, error)
        return "invalid"

    event["total_amount"] = round(
        event["quantity"] * event["unit_price"],
        2,
    )

    with get_connection() as connection:
        with connection.cursor() as cursor:
            inserted = insert_event(cursor, event)

    if inserted:
        logger.info(
            "Kafka event stored in PostgreSQL: event_id=%s",
            event["event_id"],
        )
        return "inserted"

    logger.info(
        "Duplicate Kafka event ignored: event_id=%s",
        event["event_id"],
    )
    return "duplicate"
