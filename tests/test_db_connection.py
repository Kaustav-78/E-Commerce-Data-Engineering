
import psycopg
import pytest

from app import db


def test_database_connection_failure_is_propagated(monkeypatch):
    def fake_connect(**kwargs):
        raise psycopg.OperationalError("Simulated database outage")

    monkeypatch.setattr(db.psycopg, "connect", fake_connect)

    with pytest.raises(
        psycopg.OperationalError,
        match="Simulated database outage",
    ):
        db.get_connection()

import logging

from app import processor


def test_pipeline_logs_and_propagates_database_failure(
    tmp_path, monkeypatch, caplog
):
    from app import config

    config.create_directories()

    raw_file = tmp_path / "events.jsonl"
    raw_file.write_text(
        '{"event_id":"evt-1","event_type":"order_created",'
        '"event_time":"2026-01-01T00:00:00+00:00",'
        '"order_id":"ORD000001","customer_id":"CUST0001",'
        '"product_id":"P101","quantity":1,"unit_price":499.0}\n',
        encoding="utf-8",
    )

    monkeypatch.setattr(processor, "RAW_FILE", raw_file)
    monkeypatch.setattr(
        processor,
        "PROCESSED_FILE",
        tmp_path / "valid_events.jsonl",
    )
    monkeypatch.setattr(
        processor,
        "QUARANTINE_FILE",
        tmp_path / "invalid_events.jsonl",
    )

    def fail_connection():
        import psycopg
        raise psycopg.OperationalError("Simulated database outage")

    import app.db
    monkeypatch.setattr(app.db, "get_connection", fail_connection)

    with caplog.at_level(logging.ERROR, logger="app.processor"):
        import psycopg
        with pytest.raises(psycopg.OperationalError):
            processor.process_events(load_to_db=True)

    assert "Database loading failed." in caplog.text
    assert "Simulated database outage" in caplog.text
