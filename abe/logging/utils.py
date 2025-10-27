"""Logging utilities and helper functions.

This module provides utility functions for working with the logging system,
including getting loggers, configuring handlers, and managing log levels.
"""

from __future__ import annotations

import logging
import logging.config
import os
from pathlib import Path
from typing import Any, Dict, Optional

from .settings import LoggingConfig

__all__ = [
    "get_logger",
    "setup_logging_from_config",
    "get_logging_dict_config",
    "set_logger_level",
    "get_logger_level",
    "create_log_file_path",
]


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (typically __name__).

    Returns:
        logging.Logger: Configured logger instance.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Application started")
    """
    return logging.getLogger(name)


def create_log_file_path(log_dir: str, log_file: Optional[str] = None) -> str:
    """Create and return the full path to a log file.

    Args:
        log_dir: Directory to store log files.
        log_file: Name of the log file. If None, uses "app.log".

    Returns:
        str: Full path to the log file.

    Example:
        >>> path = create_log_file_path("logs", "myapp.log")
        >>> print(path)
        logs/myapp.log
    """
    log_file = log_file or "app.log"
    os.makedirs(log_dir, exist_ok=True)
    return str(Path(log_dir) / log_file)


def get_logging_dict_config(config: LoggingConfig) -> Dict[str, Any]:
    """Generate logging configuration dictionary from LoggingConfig.

    This function creates a Python logging configuration dictionary
    that can be used with logging.config.dictConfig().

    Args:
        config: LoggingConfig instance with desired settings.

    Returns:
        Dictionary suitable for logging.config.dictConfig().

    Raises:
        ValueError: If configuration is invalid.
    """
    config.validate()

    level = config.level.upper()

    # Build formatters
    formatters: Dict[str, Dict[str, Any]] = {
        "default": {
            "format": config.format,
            "datefmt": config.date_format,
            "style": "%",
        },
    }

    # Add JSON formatter if requested and available
    if config.use_json_formatter:
        try:
            import pythonjsonlogger.jsonlogger  # noqa: F401

            formatters["json"] = {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
                "datefmt": config.date_format,
            }
        except ImportError:
            # pythonjsonlogger not available, skip JSON formatter
            pass

    # Build handlers
    handlers: Dict[str, Dict[str, Any]] = {}

    if config.enable_console:
        handlers["console"] = {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
            "level": level,
        }

    if config.enable_file or config.log_file:
        if config.log_file:
            log_file_path = config.log_file
            # Ensure directory exists for the log file
            log_dir = os.path.dirname(log_file_path)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)
        else:
            log_file_path = create_log_file_path(config.log_dir, "app.log")

        handlers["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": log_file_path,
            "maxBytes": config.max_bytes,
            "backupCount": config.backup_count,
            "encoding": config.encoding,
            "level": level,
        }

    # Build loggers configuration
    loggers: Dict[str, Dict[str, Any]] = {
        "": {  # root logger
            "handlers": list(handlers.keys()),
            "level": level,
            "propagate": config.propagate,
        },
    }

    # Add logger-specific levels
    for logger_name, logger_level in config.logger_levels.items():
        loggers[logger_name] = {
            "handlers": list(handlers.keys()),
            "level": logger_level.upper(),
            "propagate": config.propagate,
        }

    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": handlers,
        "loggers": loggers,
    }


def setup_logging_from_config(config: LoggingConfig) -> None:
    """Configure logging using LoggingConfig.

    This is the main function to set up logging in your application.

    Args:
        config: LoggingConfig instance with desired settings.

    Raises:
        ValueError: If configuration is invalid.

    Example:
        >>> config = LoggingConfig(
        ...     level="DEBUG",
        ...     log_file="/var/log/myapp.log",
        ... )
        >>> setup_logging_from_config(config)
        >>> logger = get_logger(__name__)
        >>> logger.debug("Debug message")
    """
    dict_config = get_logging_dict_config(config)
    logging.config.dictConfig(dict_config)

    # Set asyncio logger level to WARNING to reduce noise
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def set_logger_level(logger_name: str, level: str) -> None:
    """Set the level for a specific logger.

    Args:
        logger_name: Name of the logger.
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Raises:
        ValueError: If level is invalid.

    Example:
        >>> set_logger_level("urllib3", "WARNING")
        >>> set_logger_level("myapp.database", "DEBUG")
    """
    valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
    level_upper = level.upper()

    if level_upper not in valid_levels:
        raise ValueError(
            f"Invalid log level '{level}'. Must be one of {valid_levels}"
        )

    logger = logging.getLogger(logger_name)
    logger.setLevel(level_upper)


def get_logger_level(logger_name: str) -> str:
    """Get the current level of a logger.

    Args:
        logger_name: Name of the logger.

    Returns:
        str: Current logging level name (DEBUG, INFO, WARNING, ERROR, CRITICAL).

    Example:
        >>> level = get_logger_level("myapp")
        >>> print(level)
        INFO
    """
    logger = logging.getLogger(logger_name)
    return logging.getLevelName(logger.level)
