import logging
import sys
import os
from src.config.settings import settings

def setup_logging():
    """Setup structured logging for production"""
    log_level = logging.DEBUG if settings.dev_mode else logging.INFO
    
    handlers = [logging.StreamHandler(sys.stdout)]
    
    # Add file handler only in production and ensure directory exists
    if not settings.dev_mode:
        os.makedirs("logs", exist_ok=True)
        handlers.append(logging.FileHandler("logs/hrms.log"))
    
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers
    )
    
    # Set specific loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("uvicorn").setLevel(logging.INFO)