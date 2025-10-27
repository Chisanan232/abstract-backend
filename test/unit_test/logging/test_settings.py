"""Unit tests for logging settings module.

Tests the LoggingConfig dataclass and related functions.
"""

from __future__ import annotations

import pytest

from abe.logging.settings import (
    LogFormat,
    LoggingConfig,
    LogLevel,
    get_default_logging_config,
)


class TestLoggingConfig:
    """Tests for LoggingConfig dataclass."""

    def test_default_values(self) -> None:
        """Test that LoggingConfig has correct default values."""
        config = LoggingConfig()

        assert config.level == "INFO"
        assert config.format == "%(asctime)s [%(levelname)8s] %(name)s: %(message)s"
        assert config.date_format == "%Y-%m-%d %H:%M:%S"
        assert config.log_file is None
        assert config.log_dir == "logs"
        assert config.max_bytes == 10 * 1024 * 1024
        assert config.backup_count == 5
        assert config.encoding == "utf-8"
        assert config.enable_console is True
        assert config.enable_file is False
        assert config.use_json_formatter is False
        assert config.logger_levels == {}
        assert config.propagate is False

    def test_custom_values(self) -> None:
        """Test LoggingConfig with custom values."""
        config = LoggingConfig(
            level="DEBUG",
            log_file="/var/log/app.log",
            enable_file=True,
            max_bytes=50 * 1024 * 1024,
            backup_count=10,
        )

        assert config.level == "DEBUG"
        assert config.log_file == "/var/log/app.log"
        assert config.enable_file is True
        assert config.max_bytes == 50 * 1024 * 1024
        assert config.backup_count == 10

    def test_logger_levels(self) -> None:
        """Test LoggingConfig with logger-specific levels."""
        config = LoggingConfig(
            level="INFO",
            logger_levels={
                "urllib3": "WARNING",
                "requests": "ERROR",
            },
        )

        assert config.logger_levels == {
            "urllib3": "WARNING",
            "requests": "ERROR",
        }

    def test_validate_valid_level(self) -> None:
        """Test validate() with valid log level."""
        config = LoggingConfig(level="DEBUG")
        # Should not raise
        config.validate()

    def test_validate_invalid_level(self) -> None:
        """Test validate() with invalid log level."""
        config = LoggingConfig(level="INVALID")
        with pytest.raises(ValueError, match="Invalid log level"):
            config.validate()

    def test_validate_invalid_logger_level(self) -> None:
        """Test validate() with invalid logger-specific level."""
        config = LoggingConfig(
            level="INFO",
            logger_levels={"mylogger": "INVALID"},
        )
        with pytest.raises(ValueError, match="Invalid log level"):
            config.validate()

    def test_validate_negative_max_bytes(self) -> None:
        """Test validate() with negative max_bytes."""
        config = LoggingConfig(max_bytes=-1)
        with pytest.raises(ValueError, match="max_bytes must be positive"):
            config.validate()

    def test_validate_zero_max_bytes(self) -> None:
        """Test validate() with zero max_bytes."""
        config = LoggingConfig(max_bytes=0)
        with pytest.raises(ValueError, match="max_bytes must be positive"):
            config.validate()

    def test_validate_negative_backup_count(self) -> None:
        """Test validate() with negative backup_count."""
        config = LoggingConfig(backup_count=-1)
        with pytest.raises(ValueError, match="backup_count must be non-negative"):
            config.validate()

    def test_to_dict(self) -> None:
        """Test to_dict() method."""
        config = LoggingConfig(
            level="DEBUG",
            log_file="/var/log/app.log",
            logger_levels={"urllib3": "WARNING"},
        )

        config_dict = config.to_dict()

        assert isinstance(config_dict, dict)
        assert config_dict["level"] == "DEBUG"
        assert config_dict["log_file"] == "/var/log/app.log"
        assert config_dict["logger_levels"] == {"urllib3": "WARNING"}

    def test_from_dict(self) -> None:
        """Test from_dict() class method."""
        config_dict = {
            "level": "DEBUG",
            "log_file": "/var/log/app.log",
            "max_bytes": 50 * 1024 * 1024,
            "logger_levels": {"urllib3": "WARNING"},
        }

        config = LoggingConfig.from_dict(config_dict)

        assert config.level == "DEBUG"
        assert config.log_file == "/var/log/app.log"
        assert config.max_bytes == 50 * 1024 * 1024
        assert config.logger_levels == {"urllib3": "WARNING"}

    def test_from_dict_partial(self) -> None:
        """Test from_dict() with partial configuration."""
        config_dict = {
            "level": "WARNING",
            "enable_file": True,
        }

        config = LoggingConfig.from_dict(config_dict)

        assert config.level == "WARNING"
        assert config.enable_file is True
        # Other values should be defaults
        assert config.log_dir == "logs"
        assert config.backup_count == 5

    def test_round_trip_dict_conversion(self) -> None:
        """Test round-trip conversion to and from dict."""
        original = LoggingConfig(
            level="DEBUG",
            log_file="/var/log/app.log",
            max_bytes=50 * 1024 * 1024,
            logger_levels={"urllib3": "WARNING"},
        )

        config_dict = original.to_dict()
        restored = LoggingConfig.from_dict(config_dict)

        assert restored.level == original.level
        assert restored.log_file == original.log_file
        assert restored.max_bytes == original.max_bytes
        assert restored.logger_levels == original.logger_levels


class TestGetDefaultLoggingConfig:
    """Tests for get_default_logging_config() function."""

    def test_returns_logging_config(self) -> None:
        """Test that function returns LoggingConfig instance."""
        config = get_default_logging_config()
        assert isinstance(config, LoggingConfig)

    def test_returns_default_values(self) -> None:
        """Test that returned config has default values."""
        config = get_default_logging_config()

        assert config.level == "INFO"
        assert config.enable_console is True
        assert config.enable_file is False

    def test_multiple_calls_independent(self) -> None:
        """Test that multiple calls return independent instances."""
        config1 = get_default_logging_config()
        config2 = get_default_logging_config()

        # Modify one config
        config1.level = "DEBUG"

        # Other should be unchanged
        assert config2.level == "INFO"


class TestLogLevelTypeAlias:
    """Tests for LogLevel type alias."""

    def test_log_level_is_string(self) -> None:
        """Test that LogLevel is a string type."""
        level: LogLevel = "DEBUG"
        assert isinstance(level, str)

    def test_log_level_valid_values(self) -> None:
        """Test valid LogLevel values."""
        valid_levels: list[LogLevel] = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        for level in valid_levels:
            assert isinstance(level, str)


class TestLogFormatTypeAlias:
    """Tests for LogFormat type alias."""

    def test_log_format_is_string(self) -> None:
        """Test that LogFormat is a string type."""
        fmt: LogFormat = "%(asctime)s - %(name)s - %(message)s"
        assert isinstance(fmt, str)

    def test_log_format_custom_format(self) -> None:
        """Test custom log format."""
        fmt: LogFormat = "[%(levelname)s] %(message)s"
        assert isinstance(fmt, str)
