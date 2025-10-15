# -*- coding: utf-8 -*-
"""
Logging Configuration for Scheduler
"""

import logging
import logging.handlers
import os
from datetime import datetime


def setup_logging(log_dir="logs", log_level=logging.INFO):
    """
    Configure logging for the application

    Args:
        log_dir: Directory to store log files
        log_level: Logging level (default: INFO)
    """
    # Create logs directory if not exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Create formatters
    detailed_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    simple_formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s", datefmt="%H:%M:%S"
    )

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console Handler (INFO and above)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    root_logger.addHandler(console_handler)

    # File Handler - All logs (rotating)
    log_file = os.path.join(log_dir, f"scheduler_{datetime.now():%Y%m%d}.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10 MB
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(file_handler)

    # File Handler - Errors only
    error_log_file = os.path.join(log_dir, f"scheduler_errors_{datetime.now():%Y%m%d}.log")
    error_handler = logging.handlers.RotatingFileHandler(
        error_log_file, maxBytes=10 * 1024 * 1024, backupCount=5, encoding="utf-8"  # 10 MB
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(error_handler)

    # Log startup
    root_logger.info("=" * 80)
    root_logger.info("Logging system initialized")
    root_logger.info(f"Log directory: {os.path.abspath(log_dir)}")
    root_logger.info(f"Log level: {logging.getLevelName(log_level)}")
    root_logger.info("=" * 80)

    return root_logger


def get_logger(name):
    """
    Get a logger instance for a module

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance
    """
    return logging.getLogger(name)
