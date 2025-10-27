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


class TestGetLoggingDictConfigAdvanced:
    """Advanced tests for get_logging_dict_config() function."""

    def test_config_with_multiple_logger_levels(self) -> None:
        """Test config with many logger-specific levels."""
        config = LoggingConfig(
            level="INFO",
            logger_levels={
                "urllib3": "WARNING",
                "requests": "ERROR",
                "aiohttp": "WARNING",
                "asyncio": "ERROR",
                "myapp.database": "DEBUG",
                "myapp.api": "INFO",
            },
        )
        dict_config = get_logging_dict_config(config)

        # Verify all loggers are configured
        for logger_name in ["urllib3", "requests", "aiohttp", "asyncio", "myapp.database", "myapp.api"]:
            assert logger_name in dict_config["loggers"]

    def test_config_handlers_list_matches_enabled_handlers(self) -> None:
        """Test that handlers list matches enabled handlers."""
        config = LoggingConfig(enable_console=True, enable_file=False)
        dict_config = get_logging_dict_config(config)

        # Root logger should only have console handler
        root_handlers = dict_config["loggers"][""]["handlers"]
        assert "console" in root_handlers
        assert "file" not in root_handlers

    def test_config_with_both_handlers(self) -> None:
        """Test config with both console and file handlers."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            config = LoggingConfig(
                enable_console=True,
                enable_file=True,
                log_file=log_file,
            )
            dict_config = get_logging_dict_config(config)

            root_handlers = dict_config["loggers"][""]["handlers"]
            assert "console" in root_handlers
            assert "file" in root_handlers

    def test_config_handler_levels_match_root_level(self) -> None:
        """Test that handler levels match root logger level."""
        config = LoggingConfig(level="WARNING")
        dict_config = get_logging_dict_config(config)

        # All handlers should have WARNING level
        for handler_name, handler_config in dict_config["handlers"].items():
            assert handler_config["level"] == "WARNING"

    def test_config_file_handler_has_rotation_settings(self) -> None:
        """Test that file handler includes rotation settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            config = LoggingConfig(
                log_file=log_file,
                max_bytes=50 * 1024 * 1024,
                backup_count=10,
                enable_file=True,
            )
            dict_config = get_logging_dict_config(config)

            file_handler = dict_config["handlers"]["file"]
            assert file_handler["maxBytes"] == 50 * 1024 * 1024
            assert file_handler["backupCount"] == 10

    def test_config_file_handler_encoding(self) -> None:
        """Test that file handler has correct encoding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")
            config = LoggingConfig(
                log_file=log_file,
                encoding="utf-8",
                enable_file=True,
            )
            dict_config = get_logging_dict_config(config)

            file_handler = dict_config["handlers"]["file"]
            assert file_handler["encoding"] == "utf-8"

    def test_config_disable_existing_loggers_is_false(self) -> None:
        """Test that disable_existing_loggers is always False."""
        config = LoggingConfig()
        dict_config = get_logging_dict_config(config)

        assert dict_config["disable_existing_loggers"] is False

    def test_config_version_is_correct(self) -> None:
        """Test that config version is 1."""
        config = LoggingConfig()
        dict_config = get_logging_dict_config(config)

        assert dict_config["version"] == 1

    def test_config_formatters_have_required_fields(self) -> None:
        """Test that formatters have all required fields."""
        config = LoggingConfig()
        dict_config = get_logging_dict_config(config)

        default_formatter = dict_config["formatters"]["default"]
        assert "format" in default_formatter
        assert "datefmt" in default_formatter
        assert "style" in default_formatter
        assert default_formatter["style"] == "%"

    def test_config_logger_propagate_setting(self) -> None:
        """Test that logger propagate setting is applied to all loggers."""
        config = LoggingConfig(propagate=True)
        dict_config = get_logging_dict_config(config)

        # Check root logger
        assert dict_config["loggers"][""]["propagate"] is True

        # Check custom loggers
        config_with_custom = LoggingConfig(
            propagate=False,
            logger_levels={"test.logger": "DEBUG"},
        )
        dict_config_custom = get_logging_dict_config(config_with_custom)
        assert dict_config_custom["loggers"]["test.logger"]["propagate"] is False


class TestSetupLoggingFromConfigAdvanced:
    """Advanced tests for setup_logging_from_config() function."""

    def test_setup_logging_creates_valid_config(self) -> None:
        """Test that setup_logging_from_config creates valid logging config."""
        config = LoggingConfig(level="DEBUG")
        setup_logging_from_config(config)

        # Verify root logger is configured
        root_logger = logging.getLogger()
        assert root_logger is not None

    def test_setup_logging_multiple_times_reconfigures(self) -> None:
        """Test that calling setup multiple times reconfigures logging."""
        config1 = LoggingConfig(level="INFO")
        setup_logging_from_config(config1)

        logger = get_logger("test.reconfig")
        set_logger_level("test.reconfig", "INFO")
        level1 = get_logger_level("test.reconfig")

        config2 = LoggingConfig(
            level="DEBUG",
            logger_levels={"test.reconfig": "WARNING"},
        )
        setup_logging_from_config(config2)
        level2 = get_logger_level("test.reconfig")

        assert level1 == "INFO"
        assert level2 == "WARNING"

    def test_setup_logging_with_custom_format(self) -> None:
        """Test setup with custom format string."""
        custom_format = "[%(levelname)s] %(name)s: %(message)s"
        config = LoggingConfig(format=custom_format)
        setup_logging_from_config(config)

        # Verify logging is configured (no exception)
        logger = get_logger("test.custom_format")
        logger.info("Test message")

    def test_setup_logging_with_custom_date_format(self) -> None:
        """Test setup with custom date format."""
        custom_date_format = "%d/%m/%Y %H:%M:%S"
        config = LoggingConfig(date_format=custom_date_format)
        setup_logging_from_config(config)

        logger = get_logger("test.custom_date")
        logger.info("Test message")


class TestCreateLogFilePathAdvanced:
    """Advanced tests for create_log_file_path() function."""

    def test_create_log_file_path_with_nested_directories(self) -> None:
        """Test creating path with deeply nested directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_dir = os.path.join(tmpdir, "logs", "app", "debug", "2025-10")
            path = create_log_file_path(nested_dir, "app.log")

            # Directory should be created
            assert os.path.exists(nested_dir)
            assert path.endswith("app.log")

    def test_create_log_file_path_idempotent(self) -> None:
        """Test that calling create_log_file_path multiple times is safe."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path1 = create_log_file_path(tmpdir, "test.log")
            path2 = create_log_file_path(tmpdir, "test.log")

            assert path1 == path2
            assert os.path.exists(tmpdir)

    def test_create_log_file_path_returns_string(self) -> None:
        """Test that create_log_file_path returns a string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = create_log_file_path(tmpdir)
            assert isinstance(path, str)

    def test_create_log_file_path_with_special_characters(self) -> None:
        """Test creating path with special characters in filename."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = create_log_file_path(tmpdir, "app-2025-10-27.log")
            assert "app-2025-10-27.log" in path


class TestIntegrationScenarios:
    """Integration tests for common logging scenarios."""

    def test_scenario_development_environment(self) -> None:
        """Test logging setup for development environment."""
        config = LoggingConfig(
            level="DEBUG",
            enable_console=True,
            enable_file=False,
            logger_levels={
                "urllib3": "WARNING",
                "requests": "WARNING",
            },
        )
        setup_logging_from_config(config)

        dev_logger = get_logger("myapp.dev")
        dev_logger.debug("Development debug message")

    def test_scenario_production_environment(self) -> None:
        """Test logging setup for production environment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "production.log")
            config = LoggingConfig(
                level="WARNING",
                enable_console=False,
                enable_file=True,
                log_file=log_file,
                max_bytes=100 * 1024 * 1024,
                backup_count=10,
            )
            setup_logging_from_config(config)

            prod_logger = get_logger("myapp.prod")
            prod_logger.warning("Production warning")

            for handler in prod_logger.handlers:
                handler.flush()

            assert os.path.exists(log_file)

    def test_scenario_testing_environment(self) -> None:
        """Test logging setup for testing environment."""
        config = LoggingConfig(
            level="ERROR",
            enable_console=False,
            enable_file=False,
        )
        setup_logging_from_config(config)

        test_logger = get_logger("myapp.test")
        # Should not raise
        test_logger.error("Test error message")

    def test_scenario_dynamic_logger_adjustment(self) -> None:
        """Test dynamic adjustment of logger levels during runtime."""
        config = LoggingConfig(level="INFO")
        setup_logging_from_config(config)

        logger_name = "myapp.dynamic"
        logger = get_logger(logger_name)

        # Start with INFO
        set_logger_level(logger_name, "INFO")
        assert get_logger_level(logger_name) == "INFO"

        # Increase verbosity for debugging
        set_logger_level(logger_name, "DEBUG")
        assert get_logger_level(logger_name) == "DEBUG"

        # Reduce verbosity after debugging
        set_logger_level(logger_name, "WARNING")
        assert get_logger_level(logger_name) == "WARNING"
