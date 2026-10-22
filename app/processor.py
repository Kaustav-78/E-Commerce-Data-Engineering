import time
import uuid
from app.logger import get_logger

logger = get_logger(__name__)
import json

from app.config import (
    RAW_FILE,
    PROCESSED_FILE,
    QUARANTINE_FILE,
    create_directories,
)
from app.validator import validate_event


def process_events(load_to_db=False):
    """Validate, deduplicate, transform, and optionally load events."""
    create_directories()
    if not RAW_FILE.exists():
        logger.error("Raw input file not found: %s", RAW_FILE)
        raise FileNotFoundError(
            f"Raw input file not found: {RAW_FILE}"
        )
    seen_event_ids = set()
    valid_events = []

    input_count = 0
    processed_count = 0
    duplicate_count = 0
    invalid_count = 0
    run_id = str(uuid.uuid4())
    start_time = time.perf_counter()

    logger.info(
        "Starting event processing. run_id=%s",
        run_id,
    )
    with (
        RAW_FILE.open("r", encoding="utf-8") as raw_file,
        PROCESSED_FILE.open("w", encoding="utf-8") as output_file,
        QUARANTINE_FILE.open("w", encoding="utf-8") as bad_file,
    ):
        for line_number, line in enumerate(raw_file, start=1):
            input_count += 1

            try:
                event = json.loads(line)
                validate_event(event)

                event_id = event["event_id"]

                if event_id in seen_event_ids:
                    duplicate_count += 1
                    continue

                seen_event_ids.add(event_id)

                event["total_amount"] = round(
                    event["quantity"] * event["unit_price"],
                    2,
                )

                output_file.write(json.dumps(event) + "\n")
                valid_events.append(event)
                processed_count += 1

            except (json.JSONDecodeError, ValueError) as error:
                invalid_count += 1

                logger.warning(
                    "Rejected record at line %s: %s",
                    line_number,
                    error,
                )

                rejected_record = {
                    "line_number": line_number,
                    "raw_record": line.rstrip("\n"),
                    "error": str(error),
                }

                bad_file.write(json.dumps(rejected_record) + "\n")

    summary = {
        "input_records": input_count,
        "processed": processed_count,
        "duplicates": duplicate_count,
        "invalid": invalid_count,
        "success_rate_percent": round(
            processed_count / input_count * 100,
            2,
        ) if input_count else 0.0,
    }

    duration_seconds = round(time.perf_counter() - start_time, 3)

    summary["run_id"] = run_id
    summary["duration_seconds"] = duration_seconds

    logger.info(
        "Processing completed. run_id=%s duration_seconds=%s "
        "input=%s processed=%s duplicates=%s invalid=%s "
        "success_rate=%s%%",
        run_id,
        duration_seconds,
        summary["input_records"],
        summary["processed"],
        summary["duplicates"],
        summary["invalid"],
        summary["success_rate_percent"],
    )

    if load_to_db:
        from app.db import get_connection, insert_event
        import psycopg

        inserted_count = 0
        database_duplicate_count = 0

        try:
            with get_connection() as connection:
                with connection.cursor() as cursor:
                    for event in valid_events:
                        if insert_event(cursor, event):
                            inserted_count += 1
                        else:
                            database_duplicate_count += 1

        except psycopg.Error:
            logger.exception("Database loading failed.")
            raise

        summary["inserted_to_db"] = inserted_count
        summary["database_duplicates"] = database_duplicate_count

        logger.info(
            "Database loading completed: inserted=%s, database_duplicates=%s",
            inserted_count,
            database_duplicate_count,
        )

    return summary


if __name__ == "__main__":
    print(json.dumps(process_events(), indent=2))
