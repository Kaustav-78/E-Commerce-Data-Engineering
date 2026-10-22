
import json

from kafka import KafkaConsumer

from app.logger import get_logger
from app.stream_processor import process_stream_event

logger = get_logger(__name__)


def create_consumer():
    """Connect to Kafka and subscribe to order_events."""
    return KafkaConsumer(
        "order_events",
        bootstrap_servers=["localhost:9092"],
        auto_offset_reset="earliest",
        enable_auto_commit=False,
        group_id="ecommerce-postgres-consumer",
        value_deserializer=lambda value: json.loads(
            value.decode("utf-8")
        ),
        key_deserializer=lambda key: (
            key.decode("utf-8") if key else None
        ),
    )


if __name__ == "__main__":
    consumer = create_consumer()

    logger.info("Listening for Kafka order events...")

    try:
        for message in consumer:
            try:
                result = process_stream_event(message.value)

                # Commit only after the event has been handled.
                if result in ("inserted", "duplicate", "invalid"):
                    consumer.commit()
                    logger.info(
                        "Handled event: result=%s partition=%s offset=%s",
                        result,
                        message.partition,
                        message.offset,
                    )

            except Exception:
                # Do not commit this message when processing fails.
                logger.exception(
                    "Processing failed; offset not committed. "
                    "partition=%s offset=%s",
                    message.partition,
                    message.offset,
                )
                break

    except KeyboardInterrupt:
        logger.info("Consumer stopped by user.")

    finally:
        consumer.close()

