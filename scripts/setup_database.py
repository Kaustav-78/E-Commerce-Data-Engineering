from app.config import PROJECT_ROOT
from app.db import get_connection


INIT_SQL = PROJECT_ROOT / "scripts" / "init_db.sql"

EXPECTED_COLUMNS = [
    "event_id",
    "event_type",
    "event_time",
    "order_id",
    "customer_id",
    "product_id",
    "quantity",
    "unit_price",
    "total_amount",
    "ingested_at",
]


def setup_database():
    """Initialize the table if missing and verify its column order."""
    if not INIT_SQL.is_file():
        raise FileNotFoundError(f"Initialization SQL not found: {INIT_SQL}")

    sql = INIT_SQL.read_text(encoding="utf-8")

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)

            cur.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                  AND table_name = 'order_events'
                ORDER BY ordinal_position
            """)
            actual_columns = [row[0] for row in cur.fetchall()]

            if actual_columns != EXPECTED_COLUMNS:
                raise RuntimeError(
                    "order_events schema mismatch.\n"
                    f"Expected: {EXPECTED_COLUMNS}\n"
                    f"Actual:   {actual_columns}"
                )

    print("Database connection: OK")
    print("order_events column verification: OK")
    print("Database initialization completed.")


if __name__ == "__main__":
    try:
        setup_database()
    except Exception as exc:
        print(f"Database setup failed: {exc}")
        raise