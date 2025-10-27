"""Centralized logging configuration package.

This package provides a flexible, customizable logging system for the abstract-backend
library. It allows callers to easily configure logging behavior without modifying
application code.

Main Components:
    - LoggingConfig: Dataclass for customizable logging settings
    - setup_logging_from_config: Main function to configure logging
    - get_logger: Get a logger instance
    - set_logger_level: Adjust logger levels at runtime
    - get_logging_dict_config: Generate logging configuration dictionary

Example:
    >>> from abe.logging import LoggingConfig, setup_logging_from_config, get_logger
    >>>
    >>> # Create custom configuration
    >>> config = LoggingConfig(
    ...     level="DEBUG",
    ...     log_file="/var/log/myapp.log",
    ...     logger_levels={"urllib3": "WARNING"}
    ... )
    >>>
    >>> # Set up logging
    >>> setup_logging_from_config(config)
    >>>
    >>> # Get and use logger
    >>> logger = get_logger(__name__)
    >>> logger.info("Application started")
"""

from .config import (
    DEFAULT_DATE_FORMAT,
    DEFAULT_LEVEL,
    DEFAULT_LOG_DIR,
    DEFAULT_LOG_FILE,
    DEFAULT_LOG_FORMAT,
    LOG_LEVELS,
    add_logging_arguments,
    get_log_file_path,
    get_logging_config,
    setup_logging,
    setup_logging_from_args,
)
from .settings import (
    LogFormat,
    LoggingConfig,
    LogLevel,
    get_default_logging_config,
)
from .utils import (
    create_log_file_path,
    get_logger,
    get_logger_level,
    get_logging_dict_config,
    set_logger_level,
    setup_logging_from_config,
)

__all__ = [
    # Settings
    "LoggingConfig",
    "LogLevel",
    "LogFormat",
    "get_default_logging_config",
    # Utils
    "get_logger",
    "setup_logging_from_config",
    "get_logging_dict_config",
    "set_logger_level",
    "get_logger_level",
    "create_log_file_path",
    # Legacy config (for backward compatibility)
    "DEFAULT_LOG_FORMAT",
    "DEFAULT_DATE_FORMAT",
    "DEFAULT_LEVEL",
    "DEFAULT_LOG_DIR",
    "DEFAULT_LOG_FILE",
    "LOG_LEVELS",
    "get_log_file_path",
    "get_logging_config",
    "setup_logging",
    "add_logging_arguments",
    "setup_logging_from_args",
]
