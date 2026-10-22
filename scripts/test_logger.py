
from app.logger import get_logger


logger = get_logger("ecommerce_pipeline")

logger.info("Pipeline logger initialized successfully.")
logger.warning("This is a test warning.")
logger.error("This is a test error.")
