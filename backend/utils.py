import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("genai-assistant")

def read_sample_data(file_path: str = "data/sample.txt") -> str:
    """Helper function to load sample text document context."""
    if not os.path.exists(file_path):
        logger.warning(f"Sample data file not found at {file_path}")
        return ""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error reading sample data file: {e}")
        return ""

def format_error_response(error_message: str) -> dict:
    """Format an error response uniformly."""
    return {
        "status": "error",
        "message": error_message
    }
