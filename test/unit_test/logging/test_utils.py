"""Unit tests for logging utils module.

Tests utility functions for logging configuration and management.
"""

from __future__ import annotations

import logging
import os
import tempfile

import pytest

from abe.logging.settings import LoggingConfig
from abe.logging.utils import (
    create_log_file_path,
    get_logger,
    get_logger_level,
    get_logging_dict_config,
    set_logger_level,
    setup_logging_from_config,
)


class TestGetLogger:
    """Tests for get_logger() function."""

    def test_get_logger_returns_logger(self) -> None:
        """Test that get_logger returns a Logger instance."""
        logger = get_logger(__name__)
        assert isinstance(logger, logging.Logger)

    def test_get_logger_same_name_returns_same_instance(self) -> None:
        """Test that same logger name returns same instance."""
        logger1 = get_logger("test.logger")
        logger2 = get_logger("test.logger")
        assert logger1 is logger2

    def test_get_logger_different_names_different_instances(self) -> None:
        """Test that different logger names return different instances."""
        logger1 = get_logger("test.logger1")
        logger2 = get_logger("test.logger2")
        assert logger1 is not logger2

    def test_get_logger_with_module_name(self) -> None:
        """Test get_logger with typical __name__ usage."""
        logger = get_logger("abe.logging.utils")
        assert logger.name == "abe.logging.utils"


class TestCreateLogFilePath:
    """Tests for create_log_file_path() function."""

    def test_create_log_file_path_basic(self) -> None:
        """Test basic log file path creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = create_log_file_path(tmpdir)
            assert path.endswith("app.log")
            assert tmpdir in path

    def test_create_log_file_path_custom_filename(self) -> None:
        """Test log file path with custom filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = create_log_file_path(tmpdir, "myapp.log")
            assert path.endswith("myapp.log")

    def test_create_log_file_path_creates_directory(self) -> None:
        """Test that create_log_file_path creates directory if not exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = os.path.join(tmpdir, "logs", "nested")
            path = create_log_file_path(log_dir)

            # Directory should be created
            assert os.path.exists(log_dir)
            assert os.path.isdir(log_dir)

    def test_create_log_file_path_existing_directory(self) -> None:
        """Test create_log_file_path with existing directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = create_log_file_path(tmpdir)
            # Should not raise even if directory exists
            assert os.path.exists(tmpdir)


class TestGetLoggingDictConfig:
    """Tests for get_logging_dict_config() function."""

    def test_basic_config(self) -> None:
        """Test basic logging dict config generation."""
        config = LoggingConfig(level="INFO")
        dict_config = get_logging_dict_config(config)

        assert dict_config["version"] == 1
        assert dict_config["disable_existing_loggers"] is False
        assert "formatters" in dict_config
        assert "handlers" in dict_config
        assert "loggers" in dict_config

    def test_config_with_console_handler(self) -> None:
        """Test config includes console handler."""
        config = LoggingConfig(enable_console=True)
        dict_config = get_logging_dict_config(config)

        assert "console" in dict_config["handlers"]
        assert dict_config["handlers"]["console"]["class"] == "logging.StreamHandler"

    def test_config_without_console_handler(self) -> None:
        """Test config without console handler."""
        config = LoggingConfig(enable_console=False)
        dict_config = get_logging_dict_config(config)

        assert "console" not in dict_config["handlers"]

    def test_config_with_file_handler(self) -> None:
        """Test config includes file handler."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            config = LoggingConfig(log_file=log_file, enable_file=True)
            dict_config = get_logging_dict_config(config)

            assert "file" in dict_config["handlers"]
            assert dict_config["handlers"]["file"]["class"] == "logging.handlers.RotatingFileHandler"
            assert dict_config["handlers"]["file"]["filename"] == log_file

    def test_config_with_logger_levels(self) -> None:
        """Test config with logger-specific levels."""
        config = LoggingConfig(
            level="INFO",
            logger_levels={
                "urllib3": "WARNING",
                "requests": "ERROR",
            },
        )
        dict_config = get_logging_dict_config(config)

        assert "urllib3" in dict_config["loggers"]
        assert dict_config["loggers"]["urllib3"]["level"] == "WARNING"
        assert "requests" in dict_config["loggers"]
        assert dict_config["loggers"]["requests"]["level"] == "ERROR"

    def test_config_invalid_raises_error(self) -> None:
        """Test that invalid config raises ValueError."""
        config = LoggingConfig(level="INVALID")
        with pytest.raises(ValueError):
            get_logging_dict_config(config)

    def test_config_formatters_present(self) -> None:
        """Test that formatters are included in config."""
        config = LoggingConfig()
        dict_config = get_logging_dict_config(config)

        assert "default" in dict_config["formatters"]
        assert "format" in dict_config["formatters"]["default"]

    def test_config_root_logger_present(self) -> None:
        """Test that root logger is configured."""
        config = LoggingConfig(level="DEBUG")
        dict_config = get_logging_dict_config(config)

        assert "" in dict_config["loggers"]
        assert dict_config["loggers"][""]["level"] == "DEBUG"

    def test_config_propagate_setting(self) -> None:
        """Test that propagate setting is applied."""
        config = LoggingConfig(propagate=True)
        dict_config = get_logging_dict_config(config)

        assert dict_config["loggers"][""]["propagate"] is True

    def test_config_custom_format(self) -> None:
        """Test config with custom format string."""
        custom_format = "[%(levelname)s] %(message)s"
        config = LoggingConfig(format=custom_format)
        dict_config = get_logging_dict_config(config)

        assert dict_config["formatters"]["default"]["format"] == custom_format


class TestSetupLoggingFromConfig:
    """Tests for setup_logging_from_config() function."""

    def test_setup_logging_basic(self) -> None:
        """Test basic logging setup."""
        config = LoggingConfig(level="DEBUG")
        # Should not raise
        setup_logging_from_config(config)

    def test_setup_logging_with_file(self) -> None:
        """Test logging setup with file handler."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            config = LoggingConfig(
                level="INFO",
                log_file=log_file,
                enable_file=True,
            )
            setup_logging_from_config(config)

            # Verify logging is configured
            logger = logging.getLogger("test")
            assert logger is not None

    def test_setup_logging_invalid_config_raises_error(self) -> None:
        """Test that invalid config raises ValueError."""
        config = LoggingConfig(level="INVALID")
        with pytest.raises(ValueError):
            setup_logging_from_config(config)

    def test_setup_logging_sets_asyncio_level(self) -> None:
        """Test that asyncio logger level is set to WARNING."""
        config = LoggingConfig()
        setup_logging_from_config(config)

        asyncio_logger = logging.getLogger("asyncio")
        assert asyncio_logger.level == logging.WARNING


class TestSetLoggerLevel:
    """Tests for set_logger_level() function."""

    def test_set_logger_level_debug(self) -> None:
        """Test setting logger level to DEBUG."""
        logger_name = "test.set_level.debug"
        set_logger_level(logger_name, "DEBUG")

        logger = logging.getLogger(logger_name)
        assert logger.level == logging.DEBUG

    def test_set_logger_level_info(self) -> None:
        """Test setting logger level to INFO."""
        logger_name = "test.set_level.info"
        set_logger_level(logger_name, "INFO")

        logger = logging.getLogger(logger_name)
        assert logger.level == logging.INFO

    def test_set_logger_level_warning(self) -> None:
        """Test setting logger level to WARNING."""
        logger_name = "test.set_level.warning"
        set_logger_level(logger_name, "WARNING")

        logger = logging.getLogger(logger_name)
        assert logger.level == logging.WARNING

    def test_set_logger_level_error(self) -> None:
        """Test setting logger level to ERROR."""
        logger_name = "test.set_level.error"
        set_logger_level(logger_name, "ERROR")

        logger = logging.getLogger(logger_name)
        assert logger.level == logging.ERROR

    def test_set_logger_level_critical(self) -> None:
        """Test setting logger level to CRITICAL."""
        logger_name = "test.set_level.critical"
        set_logger_level(logger_name, "CRITICAL")

        logger = logging.getLogger(logger_name)
        assert logger.level == logging.CRITICAL

    def test_set_logger_level_lowercase(self) -> None:
        """Test setting logger level with lowercase string."""
        logger_name = "test.set_level.lowercase"
        set_logger_level(logger_name, "debug")

        logger = logging.getLogger(logger_name)
        assert logger.level == logging.DEBUG

    def test_set_logger_level_invalid_raises_error(self) -> None:
        """Test that invalid level raises ValueError."""
        with pytest.raises(ValueError, match="Invalid log level"):
            set_logger_level("test.logger", "INVALID")

    def test_set_logger_level_multiple_times(self) -> None:
        """Test setting logger level multiple times."""
        logger_name = "test.set_level.multiple"

        set_logger_level(logger_name, "DEBUG")
        logger = logging.getLogger(logger_name)
        assert logger.level == logging.DEBUG

        set_logger_level(logger_name, "WARNING")
        assert logger.level == logging.WARNING


class TestGetLoggerLevel:
    """Tests for get_logger_level() function."""

    def test_get_logger_level_returns_string(self) -> None:
        """Test that get_logger_level returns string."""
        logger_name = "test.get_level.string"
        set_logger_level(logger_name, "DEBUG")

        level = get_logger_level(logger_name)
        assert isinstance(level, str)

    def test_get_logger_level_debug(self) -> None:
        """Test getting DEBUG level."""
        logger_name = "test.get_level.debug"
        set_logger_level(logger_name, "DEBUG")

        level = get_logger_level(logger_name)
        assert level == "DEBUG"

    def test_get_logger_level_info(self) -> None:
        """Test getting INFO level."""
        logger_name = "test.get_level.info"
        set_logger_level(logger_name, "INFO")

        level = get_logger_level(logger_name)
        assert level == "INFO"

    def test_get_logger_level_warning(self) -> None:
        """Test getting WARNING level."""
        logger_name = "test.get_level.warning"
        set_logger_level(logger_name, "WARNING")

        level = get_logger_level(logger_name)
        assert level == "WARNING"

    def test_get_logger_level_error(self) -> None:
        """Test getting ERROR level."""
        logger_name = "test.get_level.error"
        set_logger_level(logger_name, "ERROR")

        level = get_logger_level(logger_name)
        assert level == "ERROR"

    def test_get_logger_level_critical(self) -> None:
        """Test getting CRITICAL level."""
        logger_name = "test.get_level.critical"
        set_logger_level(logger_name, "CRITICAL")

        level = get_logger_level(logger_name)
        assert level == "CRITICAL"

    def test_get_logger_level_unset_logger(self) -> None:
        """Test getting level of logger that hasn't been explicitly set."""
        logger_name = "test.get_level.unset"
        level = get_logger_level(logger_name)
        # Should return a valid level name
        assert isinstance(level, str)
        assert level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL", "NOTSET"]
