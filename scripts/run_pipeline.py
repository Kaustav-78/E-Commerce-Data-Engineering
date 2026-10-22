
import json

from app.config import RAW_FILE, create_directories
from app.event_generator import generate_events, write_raw_events
from app.processor import process_events


def main():
    # Prepare the required directories.
    create_directories()

    # Generate 100 orders plus test records.
    events = generate_events(count=100, seed=42)
    write_raw_events(events)

    print(f"Raw events saved to: {RAW_FILE}")
    print(f"Total input records: {len(events)}")

    # Run the processing pipeline.
    summary = process_events(load_to_db=True)

    print("\nPipeline execution completed.")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
