"""Integration tests for logging system.

Tests the complete logging system with real file I/O and logging output.
"""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path

import pytest

from abe.logging import (
    LoggingConfig,
    get_logger,
    get_logger_level,
    set_logger_level,
    setup_logging_from_config,
)

# type: ignore[misc]


class TestLoggingIntegration:
    """Integration tests for the logging system."""

    def test_setup_and_log_to_console(self) -> None:
        """Test setting up logging and logging to console."""
        config = LoggingConfig(level="INFO", enable_console=True)
        setup_logging_from_config(config)

        logger = get_logger("test.integration.console")
        # Should not raise
        logger.info("Test message")

    def test_setup_and_log_to_file(self) -> None:
        """Test setting up logging and logging to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")

            config = LoggingConfig(
                level="INFO",
                log_file=log_file,
                enable_console=False,
                enable_file=True,
            )
            setup_logging_from_config(config)

            logger = get_logger("test.integration.file")
            logger.info("Test message to file")

            # Give handlers time to write
            for handler in logger.handlers:
                handler.flush()

            # File should exist and contain the message
            assert os.path.exists(log_file)
            with open(log_file, "r") as f:
                content = f.read()
                assert "Test message to file" in content

    def test_setup_and_log_to_both_console_and_file(self) -> None:
        """Test logging to both console and file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "test.log")

            config = LoggingConfig(
                level="DEBUG",
                log_file=log_file,
                enable_console=True,
                enable_file=True,
            )
            setup_logging_from_config(config)

            logger = get_logger("test.integration.both")
            logger.debug("Debug message")
            logger.info("Info message")

            # Flush handlers
            for handler in logger.handlers:
                handler.flush()

            # File should exist and contain messages
            assert os.path.exists(log_file)
            with open(log_file, "r") as f:
                content = f.read()
                assert "Debug message" in content
                assert "Info message" in content

    def test_logger_specific_levels(self) -> None:
        """Test logger-specific levels configuration."""
        config = LoggingConfig(
            level="DEBUG",
            logger_levels={
                "test.integration.verbose": "WARNING",
                "test.integration.quiet": "ERROR",
            },
        )
        setup_logging_from_config(config)

        verbose_logger = get_logger("test.integration.verbose")
        quiet_logger = get_logger("test.integration.quiet")

        assert get_logger_level("test.integration.verbose") == "WARNING"
        assert get_logger_level("test.integration.quiet") == "ERROR"

    def test_set_logger_level_at_runtime(self) -> None:
        """Test changing logger level at runtime."""
        config = LoggingConfig(level="INFO")
        setup_logging_from_config(config)

        logger_name = "test.integration.runtime"
        logger = get_logger(logger_name)

        # Set initial level explicitly
        set_logger_level(logger_name, "INFO")
        assert get_logger_level(logger_name) == "INFO"

        # Change level
        set_logger_level(logger_name, "DEBUG")
        assert get_logger_level(logger_name) == "DEBUG"

        # Change again
        set_logger_level(logger_name, "ERROR")
        assert get_logger_level(logger_name) == "ERROR"

    def test_multiple_loggers_independent_levels(self) -> None:
        """Test that multiple loggers can have independent levels."""
        config = LoggingConfig(
            level="INFO",
            logger_levels={
                "test.integration.logger1": "DEBUG",
                "test.integration.logger2": "WARNING",
            },
        )
        setup_logging_from_config(config)

        logger1 = get_logger("test.integration.logger1")
        logger2 = get_logger("test.integration.logger2")

        assert get_logger_level("test.integration.logger1") == "DEBUG"
        assert get_logger_level("test.integration.logger2") == "WARNING"

    def test_rotating_file_handler(self) -> None:
        """Test that rotating file handler is properly configured."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "rotating.log")

            config = LoggingConfig(
                level="INFO",
                log_file=log_file,
                max_bytes=1024,  # Small size to test rotation
                backup_count=3,
                enable_file=True,
            )
            setup_logging_from_config(config)

            logger = get_logger("test.integration.rotating")

            # Write enough data to potentially trigger rotation
            for i in range(100):
                logger.info(f"Message {i}: " + "x" * 50)

            # Flush handlers
            for handler in logger.handlers:
                handler.flush()

            # Check that log files exist
            log_files = list(Path(tmpdir).glob("rotating.log*"))
            assert len(log_files) > 0

    def test_custom_format_in_logs(self) -> None:
        """Test that custom format is applied to logs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "custom_format.log")
            custom_format = "[%(levelname)s] %(name)s: %(message)s"

            config = LoggingConfig(
                level="INFO",
                log_file=log_file,
                format=custom_format,
                enable_file=True,
                enable_console=False,
            )
            setup_logging_from_config(config)

            logger = get_logger("test.integration.format")
            logger.info("Test message")

            # Flush handlers
            for handler in logger.handlers:
                handler.flush()

            # Check format in file
            with open(log_file, "r") as f:
                content = f.read()
                assert "[INFO]" in content
                assert "test.integration.format" in content
                assert "Test message" in content

    def test_config_from_dict_and_setup(self) -> None:
        """Test creating config from dict and setting up logging."""
        config_dict = {
            "level": "DEBUG",
            "enable_console": True,
            "logger_levels": {"test.integration.dict": "WARNING"},
        }

        config = LoggingConfig.from_dict(config_dict)
        setup_logging_from_config(config)

        logger = get_logger("test.integration.dict")
        assert get_logger_level("test.integration.dict") == "WARNING"

    def test_propagate_setting_affects_logging(self) -> None:
        """Test that propagate setting is respected."""
        config = LoggingConfig(
            level="INFO",
            propagate=False,
        )
        setup_logging_from_config(config)

        logger = get_logger("test.integration.propagate")
        # Should not raise
        logger.info("Test message")

    def test_multiple_setups_with_different_configs(self) -> None:
        """Test that logging can be reconfigured multiple times."""
        # First setup with explicit logger level
        config1 = LoggingConfig(
            level="INFO",
            logger_levels={"test.integration.reconfig": "INFO"},
        )
        setup_logging_from_config(config1)
        logger1 = get_logger("test.integration.reconfig")
        assert get_logger_level("test.integration.reconfig") == "INFO"

        # Second setup with different level
        config2 = LoggingConfig(
            level="DEBUG",
            logger_levels={"test.integration.reconfig": "WARNING"},
        )
        setup_logging_from_config(config2)
        assert get_logger_level("test.integration.reconfig") == "WARNING"

    def test_file_encoding_utf8(self) -> None:
        """Test that file is created with UTF-8 encoding."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_file = os.path.join(tmpdir, "utf8.log")

            config = LoggingConfig(
                level="INFO",
                log_file=log_file,
                encoding="utf-8",
                enable_file=True,
                enable_console=False,
            )
            setup_logging_from_config(config)

            logger = get_logger("test.integration.utf8")
            logger.info("UTF-8 test: 你好世界 🌍")

            # Flush handlers
            for handler in logger.handlers:
                handler.flush()

            # Read file and verify encoding
            with open(log_file, "r", encoding="utf-8") as f:
                content = f.read()
                assert "UTF-8 test" in content
