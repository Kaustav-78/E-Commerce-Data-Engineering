
from pathlib import Path

# Find the project root directory.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Define the data directories.
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
QUARANTINE_DIR = DATA_DIR / "quarantine"

# Define the data files.
RAW_FILE = RAW_DIR / "events.jsonl"
PROCESSED_FILE = PROCESSED_DIR / "valid_events.jsonl"
QUARANTINE_FILE = QUARANTINE_DIR / "invalid_events.jsonl"


def create_directories():
    """Create required directories if they do not exist."""
    for directory in (RAW_DIR, PROCESSED_DIR, QUARANTINE_DIR):
        directory.mkdir(parents=True, exist_ok=True)
