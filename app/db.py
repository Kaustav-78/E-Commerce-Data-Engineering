
import os

import psycopg
from dotenv import load_dotenv

from app.config import PROJECT_ROOT

load_dotenv(PROJECT_ROOT / ".env")


def get_connection():
    """Open a connection to the ecommerce PostgreSQL database."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "5432")),
        dbname=os.getenv("DB_NAME", "ecommerce_db"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.environ["DB_PASSWORD"],
    )


def insert_event(cursor, event):
    """
    Insert one validated event.

    Return True if inserted, or False if its event_id already exists.
    """
    query = """
        INSERT INTO order_events (
            event_id,
            event_type,
            event_time,
            order_id,
            customer_id,
            product_id,
            quantity,
            unit_price,
            total_amount
        )
        VALUES (
            %(event_id)s,
            %(event_type)s,
            %(event_time)s,
            %(order_id)s,
            %(customer_id)s,
            %(product_id)s,
            %(quantity)s,
            %(unit_price)s,
            %(total_amount)s
        )
        ON CONFLICT (event_id) DO NOTHING
        RETURNING event_id;
    """

    cursor.execute(query, event)
    return cursor.fetchone() is not None

