CREATE TABLE IF NOT EXISTS public.order_events (
    event_id VARCHAR PRIMARY KEY,
    event_type VARCHAR NOT NULL,
    event_time TIMESTAMPTZ NOT NULL,
    order_id VARCHAR NOT NULL,
    customer_id VARCHAR NOT NULL,
    product_id VARCHAR NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price NUMERIC NOT NULL,
    total_amount NUMERIC NOT NULL,
    ingested_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
);