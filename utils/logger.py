"""
Logging configuration για AI Document Analyzer
"""
from loguru import logger
import sys
from config import config

def setup_logger():
    """Ρύθμιση logging συστήματος"""
    
    # Αφαίρεση default handler
    logger.remove()
    
    # Console logging
    logger.add(
        sys.stdout,
        format=config.LOG_FORMAT,
        level=config.LOG_LEVEL,
        colorize=True
    )
    
    # File logging
    logger.add(
        config.LOGS_DIR / "app_{time:YYYY-MM-DD}.log",
        format=config.LOG_FORMAT,
        level=config.LOG_LEVEL,
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )
    
    # Error logging
    logger.add(
        config.LOGS_DIR / "errors_{time:YYYY-MM-DD}.log",
        format=config.LOG_FORMAT,
        level="ERROR",
        rotation="1 day",
        retention="90 days"
    )
    
    return logger
