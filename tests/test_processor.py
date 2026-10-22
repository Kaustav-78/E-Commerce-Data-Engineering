
import json

from app import processor
from app.event_generator import generate_event


def test_pipeline_deduplicates_and_quarantines(
    tmp_path, monkeypatch
):
    raw_file = tmp_path / "events.jsonl"
    output_file = tmp_path / "valid.jsonl"
    quarantine_file = tmp_path / "invalid.jsonl"

    valid = generate_event(1)
    duplicate = valid.copy()

    invalid = generate_event(2)
    invalid["quantity"] = -3

    records = [valid, duplicate, invalid]

    raw_file.write_text(
        "".join(json.dumps(r) + "\n" for r in records),
        encoding="utf-8",
    )

    monkeypatch.setattr(processor, "RAW_FILE", raw_file)
    monkeypatch.setattr(processor, "PROCESSED_FILE", output_file)
    monkeypatch.setattr(
        processor, "QUARANTINE_FILE", quarantine_file
    )

    summary = processor.process_events()

    assert summary["input_records"] == 3
    assert summary["processed"] == 1
    assert summary["duplicates"] == 1
    assert summary["invalid"] == 1
    assert summary["success_rate_percent"] == 33.33

    assert "run_id" in summary
    assert len(summary["run_id"]) == 36

    assert isinstance(summary["duration_seconds"], float)
    assert summary["duration_seconds"] >= 0

    output = [
        json.loads(line)
        for line in output_file.read_text(
            encoding="utf-8"
        ).splitlines()
    ]

    rejected = [
        json.loads(line)
        for line in quarantine_file.read_text(
            encoding="utf-8"
        ).splitlines()
    ]

    assert len(output) == 1
    assert output[0]["total_amount"] == (
        valid["quantity"] * valid["unit_price"]
    )
    assert len(rejected) == 1
    assert "error" in rejected[0]

import pytest

from app.processor import process_events


def test_missing_raw_file_raises_clear_error(tmp_path, monkeypatch):
    from app import processor

    missing_file = tmp_path / "missing_events.jsonl"
    monkeypatch.setattr(processor, "RAW_FILE", missing_file)

    with pytest.raises(FileNotFoundError, match="Raw input file not found"):
        process_events()
