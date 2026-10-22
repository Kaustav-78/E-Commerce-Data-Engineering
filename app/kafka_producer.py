
import json

from kafka import KafkaProducer


def create_producer():
    """Connect to the local Kafka broker."""
    return KafkaProducer(
        bootstrap_servers=["localhost:9092"],
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        key_serializer=lambda key: key.encode("utf-8"),
        acks="all",
        retries=5,
    )


def publish_event(producer, event):
    """Publish one event to the order_events topic."""
    future = producer.send(
        "order_events",
        key=event["event_id"],
        value=event,
    )

    metadata = future.get(timeout=10)

    print(
        f"Published event_id={event['event_id']} "
        f"topic={metadata.topic} "
        f"partition={metadata.partition} "
        f"offset={metadata.offset}"
    )


if __name__ == "__main__":
    producer = create_producer()

    try:
        event = {
            "event_id": "kafka-test-003",
            "event_type": "order_created",
            "event_time": "2026-10-22T16:25:00+00:00",
            "order_id": "ORD-KAFKA-003",
            "customer_id": "CUST0001",
            "product_id": "P101",
            "quantity": 2,
            "unit_price": 499.00,
        }

        publish_event(producer, event)

    finally:
        producer.close()
