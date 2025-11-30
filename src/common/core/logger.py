"""Logging configuration for Reachy Mini apps."""

import logging
import sys
from typing import Optional


def setup_logger(
    name: str,
    level: str = "INFO",
    format_str: Optional[str] = None,
) -> logging.Logger:
    """Set up a logger with consistent formatting.
    
    Args:
        name: Logger name (typically __name__ from the calling module)
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_str: Custom format string (optional)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Avoid adding handlers if they already exist
    if logger.handlers:
        return logger
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    
    if format_str is None:
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    formatter = logging.Formatter(format_str)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger
