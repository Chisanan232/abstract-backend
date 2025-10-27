"""Logging configuration settings and customization.

This module provides a flexible, customizable logging configuration system
that allows callers to easily adjust logging behavior without modifying
the application code.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

__all__ = [
    "LogLevel",
    "LogFormat",
    "LoggingConfig",
    "get_default_logging_config",
]

# Supported log levels
LogLevel = str
"""Type alias for logging level strings (DEBUG, INFO, WARNING, ERROR, CRITICAL)."""

# Supported log formats
LogFormat = str
"""Type alias for logging format strings."""


@dataclass
class LoggingConfig:
    """Customizable logging configuration.

    This class provides a structured way to configure logging behavior
    with sensible defaults that can be easily overridden.

    Attributes:
        level: Root logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
               Default: INFO
        format: Log message format string. Default uses timestamp, level, logger name, and message.
        date_format: Date format string for log timestamps. Default: ISO 8601 format.
        log_file: Path to log file. If None, logs to console only.
        log_dir: Directory for log files. Default: "logs"
        max_bytes: Maximum size of log file before rotation (in bytes). Default: 10MB
        backup_count: Number of backup log files to keep. Default: 5
        encoding: Encoding for log files. Default: utf-8
        enable_console: Whether to log to console. Default: True
        enable_file: Whether to log to file. Default: False (set True if log_file is provided)
        use_json_formatter: Whether to use JSON formatter (if pythonjsonlogger available). Default: False
        logger_levels: Dict of logger-specific levels. Useful for reducing noise from external libraries.
        propagate: Whether to propagate logs to parent loggers. Default: False

    Example:
        >>> # Basic configuration with custom level
        >>> config = LoggingConfig(level="DEBUG")
        >>>
        >>> # Configuration with file logging
        >>> config = LoggingConfig(
        ...     level="INFO",
        ...     log_file="/var/log/myapp.log",
        ...     max_bytes=50 * 1024 * 1024,  # 50MB
        ... )
        >>>
        >>> # Configuration with logger-specific levels
        >>> config = LoggingConfig(
        ...     level="DEBUG",
        ...     logger_levels={
        ...         "urllib3": "WARNING",
        ...         "requests": "WARNING",
        ...     }
        ... )
    """

    level: LogLevel = "INFO"
    """Root logging level."""

    format: LogFormat = "%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
    """Log message format string."""

    date_format: str = "%Y-%m-%d %H:%M:%S"
    """Date format for log timestamps."""

    log_file: Optional[str] = None
    """Path to log file. If None, logs to console only."""

    log_dir: str = "logs"
    """Directory for log files."""

    max_bytes: int = 10 * 1024 * 1024
    """Maximum size of log file before rotation (in bytes). Default: 10MB"""

    backup_count: int = 5
    """Number of backup log files to keep."""

    encoding: str = "utf-8"
    """Encoding for log files."""

    enable_console: bool = True
    """Whether to log to console."""

    enable_file: bool = False
    """Whether to log to file."""

    use_json_formatter: bool = False
    """Whether to use JSON formatter (if pythonjsonlogger available)."""

    logger_levels: Dict[str, LogLevel] = field(default_factory=dict)
    """Dict of logger-specific levels for fine-grained control."""

    propagate: bool = False
    """Whether to propagate logs to parent loggers."""

    def validate(self) -> None:
        """Validate the configuration.

        Raises:
            ValueError: If configuration is invalid.
        """
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

        # Validate root level
        if self.level.upper() not in valid_levels:
            raise ValueError(
                f"Invalid log level '{self.level}'. Must be one of {valid_levels}"
            )

        # Validate logger-specific levels
        for logger_name, level in self.logger_levels.items():
            if level.upper() not in valid_levels:
                raise ValueError(
                    f"Invalid log level '{level}' for logger '{logger_name}'. "
                    f"Must be one of {valid_levels}"
                )

        # Validate file-related settings
        if self.max_bytes <= 0:
            raise ValueError(f"max_bytes must be positive, got {self.max_bytes}")

        if self.backup_count < 0:
            raise ValueError(f"backup_count must be non-negative, got {self.backup_count}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary.

        Returns:
            Dictionary representation of the configuration.
        """
        return {
            "level": self.level,
            "format": self.format,
            "date_format": self.date_format,
            "log_file": self.log_file,
            "log_dir": self.log_dir,
            "max_bytes": self.max_bytes,
            "backup_count": self.backup_count,
            "encoding": self.encoding,
            "enable_console": self.enable_console,
            "enable_file": self.enable_file,
            "use_json_formatter": self.use_json_formatter,
            "logger_levels": self.logger_levels,
            "propagate": self.propagate,
        }

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> LoggingConfig:
        """Create configuration from dictionary.

        Args:
            config_dict: Dictionary with configuration values.

        Returns:
            LoggingConfig instance.
        """
        return cls(**config_dict)


def get_default_logging_config() -> LoggingConfig:
    """Get default logging configuration.

    Returns:
        LoggingConfig with default values.
    """
    return LoggingConfig()
