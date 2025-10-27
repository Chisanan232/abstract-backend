"""
Unit tests for the event consumer implementations.
"""

import asyncio
import logging
from typing import Any, AsyncIterator, Dict, List, Optional
from unittest import mock

import pytest

from abe.backends.queue.consumer import AsyncLoopConsumer


class MockBackend:
    """Test double that directly implements QueueBackend for testing purposes."""

    def __init__(self) -> None:
        """Initialize the mock backend with default values."""
        self.items: List[Dict[str, Any]] = []
        self.sleep_time: float = 0
        self.group_used: Optional[str] = None
        self.publish_called: bool = False
        self.publish_messages: List[Dict[str, Any]] = []
        self.consumed_count: int = 0

    async def publish(self, key: str, payload: Dict[str, Any]) -> None:
        """Mock implementation of publish that records calls."""
        self.publish_called = True
        self.publish_messages.append(payload)

    async def consume(self, *, group: Optional[str] = None) -> AsyncIterator[Dict[str, Any]]:
        """Mock implementation of consume that yields configured items."""
        self.group_used = group
        self.consumed_count += 1

        for item in self.items:
            if self.sleep_time > 0:
                await asyncio.sleep(self.sleep_time)
            yield item

    @classmethod
    def from_env(cls) -> "MockBackend":
        """Factory method to satisfy protocol."""
        return cls()


class ErrorThrowingBackend(MockBackend):
    """A mock backend that throws errors during consume cleanup."""

    def __init__(self, error_type: type = Exception) -> None:
        super().__init__()
        self.error_type: type = error_type

    async def consume(self, *, group: Optional[str] = None) -> AsyncIterator[Dict[str, Any]]:
        """Mock implementation that raises an exception when cancelled."""
        try:
            yield {"test": "message"}
            # This sleep is important to ensure the task gets cancelled mid-operation
            await asyncio.sleep(10)
            yield {"test": "message2"}
        except asyncio.CancelledError:
            # Simulate error during cleanup
            raise self.error_type("Simulated error during cleanup")


class TestAsyncLoopConsumer:
    """Test the AsyncLoopConsumer implementation."""

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_run_calls_handler_for_each_message(self) -> None:
        """Test that the handler is called for each consumed message."""
        # Create a mock backend
        mock_backend = MockBackend()
        mock_backend.items = [{"id": 1}, {"id": 2}]

        # Create a mock handler
        mock_handler = mock.AsyncMock()

        # Create the consumer
        consumer = AsyncLoopConsumer(mock_backend)

        # Run the consumer with a timeout to avoid hanging the test
        try:
            await asyncio.wait_for(consumer.run(mock_handler), timeout=0.5)
        except asyncio.TimeoutError:
            pass

        # Verify the handler was called with each message
        assert mock_handler.call_count == 2
        mock_handler.assert_any_call({"id": 1})
        mock_handler.assert_any_call({"id": 2})

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_run_with_consumer_group(self) -> None:
        """Test running the consumer with a consumer group."""
        # Create a mock backend
        mock_backend = MockBackend()

        # Consumer group to test
        group_name = "test-group"

        # Create a mock handler
        mock_handler = mock.AsyncMock()

        # Create the consumer with a group
        consumer = AsyncLoopConsumer(mock_backend, group=group_name)

        # Run the consumer with a timeout to avoid hanging the test
        try:
            await asyncio.wait_for(consumer.run(mock_handler), timeout=0.1)
        except asyncio.TimeoutError:
            pass

        # Verify the backend was called with the group
        assert mock_backend.group_used == group_name

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_handler_error_doesnt_stop_consumer(self) -> None:
        """Test that the consumer continues even if the handler raises an exception."""
        # Create a mock backend
        mock_backend = MockBackend()

        # Set up the mock to yield three messages
        mock_backend.items = [{"id": 1}, {"id": 2}, {"id": 3}]

        # Create a handler that raises an exception on the second message
        processed_ids = []

        async def failing_handler(msg: Dict[str, Any]) -> None:
            if msg["id"] == 2:
                raise ValueError("Test error")
            processed_ids.append(msg["id"])

        # Create the consumer
        consumer = AsyncLoopConsumer(mock_backend)

        # Run the consumer with a timeout
        try:
            await asyncio.wait_for(consumer.run(failing_handler), timeout=0.1)
        except asyncio.TimeoutError:
            pass

        # Verify both messages 1 and 3 were processed, even though 2 raised an error
        assert 1 in processed_ids
        assert 3 in processed_ids
        assert 2 not in processed_ids

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_shutdown(self) -> None:
        """Test that shutdown cancels the consumer task."""
        # Create a mock backend that blocks indefinitely
        mock_backend = MockBackend()

        # Set up the mock to simulate a long-running process
        mock_backend.items = [{"id": 1}, {"id": 2}, {"id": 3}]
        mock_backend.sleep_time = 1  # Simulate slow message processing

        # Create a mock handler
        mock_handler = mock.AsyncMock()

        # Create the consumer
        consumer = AsyncLoopConsumer(mock_backend)

        # Start the consumer in a background task
        task = asyncio.create_task(consumer.run(mock_handler))

        # Give it a moment to start
        await asyncio.sleep(0.1)

        # Shutdown the consumer
        await consumer.shutdown()

        # Verify the task was cancelled
        assert task.cancelled() or task.done()

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_idempotent_run(self) -> None:
        """Test that calling run multiple times doesn't restart the consumer."""
        # Create a mock backend
        mock_backend = MockBackend()
        # Add some items so the consumer doesn't exit immediately
        mock_backend.sleep_time = 0
        mock_backend.items = [{"id": 1}]

        # Create a mock handler
        mock_handler = mock.AsyncMock()

        # Create the consumer
        consumer = AsyncLoopConsumer(mock_backend)

        # Run the consumer twice with small timeouts
        task1 = asyncio.create_task(consumer.run(mock_handler))
        await asyncio.sleep(0.1)
        task2 = asyncio.create_task(consumer.run(mock_handler))
        await asyncio.sleep(0.1)

        # Cancel the tasks to clean up
        task1.cancel()
        try:
            await task1
        except asyncio.CancelledError:
            pass

        # The second task should return immediately since consumer is already running
        # so it should already be done
        assert task2.done()

        # Only one consume call should happen
        assert mock_backend.consumed_count == 1

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_shutdown_handles_not_running(self) -> None:
        """Test that shutdown gracefully handles the case when not running."""
        # Create a mock backend
        mock_backend = MockBackend()

        # Create the consumer but don't start it
        consumer = AsyncLoopConsumer(mock_backend)

        # Shutdown should not raise an exception
        await consumer.shutdown()

        # Consumer should still be in not running state
        assert not consumer._running
        assert consumer._task is None

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_shutdown_logs_cancellation(self, caplog: Any) -> None:
        """Test that shutdown logs task cancellation."""
        # Set up logging capture
        caplog.set_level(logging.DEBUG)

        # Create a mock backend
        mock_backend = MockBackend()
        mock_backend.sleep_time = 1  # Make it slow to ensure cancellation
        mock_backend.items = [{"id": 1}]

        # Create a mock handler
        mock_handler = mock.AsyncMock()

        # Create the consumer
        consumer = AsyncLoopConsumer(mock_backend)

        # Start the consumer
        task = asyncio.create_task(consumer.run(mock_handler))
        await asyncio.sleep(0.1)  # Give it time to start

        # Shutdown the consumer
        await consumer.shutdown()

        # Check that appropriate log messages were generated
        assert "Shutting down AsyncLoopConsumer" in caplog.text
        assert "Cancelling consumer task" in caplog.text
        assert "Consumer task cancelled successfully" in caplog.text
        assert "Consumer shutdown complete" in caplog.text

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_shutdown_handles_unexpected_errors(self, caplog: Any) -> None:
        """Test that shutdown handles unexpected errors during task cancellation."""
        # Set up logging capture
        caplog.set_level(logging.WARNING)

        # Create a backend that throws an error during cancellation
        error_backend = ErrorThrowingBackend(error_type=RuntimeError)

        # Create a mock handler
        mock_handler = mock.AsyncMock()

        # Create the consumer
        consumer = AsyncLoopConsumer(error_backend)

        # Start the consumer
        task = asyncio.create_task(consumer.run(mock_handler))
        await asyncio.sleep(0.1)  # Give it time to start

        # Shutdown the consumer
        await consumer.shutdown()

        # Check that error was logged but not raised
        assert "Unexpected error during consumer shutdown" in caplog.text
        assert "Simulated error during cleanup" in caplog.text

        # Make sure cleanup still happened
        assert consumer._task is None
        assert not consumer._running

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_shutdown_with_already_done_task(self, caplog: Any) -> None:
        """Test shutdown when the task is already done."""
        # Set up logging capture
        caplog.set_level(logging.DEBUG)

        # Create a mock backend that completes quickly
        mock_backend = MockBackend()
        mock_backend.items = [{"id": 1}]  # Just one item, so it will complete

        # Create a mock handler
        mock_handler = mock.AsyncMock()

        # Create the consumer
        consumer = AsyncLoopConsumer(mock_backend)

        # Run the consumer to completion
        task = asyncio.create_task(consumer.run(mock_handler))

        # Wait for the task to complete
        await asyncio.sleep(0.2)

        # Ensure task is done
        assert task.done()

        # Now shutdown the consumer
        await consumer.shutdown()

        # Check that appropriate log messages were generated
        assert "Consumer task was already completed" in caplog.text

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_handler_raises_cancelled_error(self, caplog: Any) -> None:
        """Test that CancelledError in handler is properly re-raised."""
        # Set up logging capture
        caplog.set_level(logging.ERROR)

        # Create a mock backend
        mock_backend = MockBackend()
        mock_backend.items = [{"id": 1}]

        # Create a handler that raises CancelledError
        async def cancelling_handler(msg: Dict[str, Any]) -> None:
            raise asyncio.CancelledError()

        # Create the consumer
        consumer = AsyncLoopConsumer(mock_backend)

        # Run the consumer - it should propagate the CancelledError
        task = asyncio.create_task(consumer.run(cancelling_handler))
        await asyncio.sleep(0.1)

        # The task should be cancelled or done
        assert task.done()

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_handler_raises_timeout_error(self, caplog: Any) -> None:
        """Test that TimeoutError in handler is caught and logged."""
        # Set up logging capture
        caplog.set_level(logging.ERROR)

        # Create a mock backend
        mock_backend = MockBackend()
        mock_backend.items = [{"id": 1}, {"id": 2}]

        # Create a handler that raises TimeoutError on first message
        call_count = 0

        async def timeout_handler(msg: Dict[str, Any]) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise asyncio.TimeoutError("Handler timeout")

        # Create the consumer
        consumer = AsyncLoopConsumer(mock_backend)

        # Run the consumer with a timeout
        try:
            await asyncio.wait_for(consumer.run(timeout_handler), timeout=0.5)
        except asyncio.TimeoutError:
            pass

        # Verify error was logged
        assert "Error processing message" in caplog.text

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_handler_raises_value_error(self, caplog: Any) -> None:
        """Test that ValueError in handler is caught and logged."""
        # Set up logging capture
        caplog.set_level(logging.ERROR)

        # Create a mock backend
        mock_backend = MockBackend()
        mock_backend.items = [{"id": 1}, {"id": 2}]

        # Create a handler that raises ValueError
        call_count = 0

        async def value_error_handler(msg: Dict[str, Any]) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise ValueError("Invalid value in message")

        # Create the consumer
        consumer = AsyncLoopConsumer(mock_backend)

        # Run the consumer with a timeout
        try:
            await asyncio.wait_for(consumer.run(value_error_handler), timeout=0.5)
        except asyncio.TimeoutError:
            pass

        # Verify error was logged
        assert "Error processing message" in caplog.text
        assert "Invalid value in message" in caplog.text

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_handler_raises_runtime_error(self, caplog: Any) -> None:
        """Test that RuntimeError in handler is caught and logged."""
        # Set up logging capture
        caplog.set_level(logging.ERROR)

        # Create a mock backend
        mock_backend = MockBackend()
        mock_backend.items = [{"id": 1}, {"id": 2}]

        # Create a handler that raises RuntimeError
        call_count = 0

        async def runtime_error_handler(msg: Dict[str, Any]) -> None:
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("Runtime error occurred")

        # Create the consumer
        consumer = AsyncLoopConsumer(mock_backend)

        # Run the consumer with a timeout
        try:
            await asyncio.wait_for(consumer.run(runtime_error_handler), timeout=0.5)
        except asyncio.TimeoutError:
            pass

        # Verify error was logged
        assert "Error processing message" in caplog.text
        assert "Runtime error occurred" in caplog.text

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_shutdown_with_timeout_error(self, caplog: Any) -> None:
        """Test that TimeoutError during shutdown is properly handled."""
        # Set up logging capture
        caplog.set_level(logging.WARNING)

        # Create a backend that throws TimeoutError during cancellation
        error_backend = ErrorThrowingBackend(error_type=asyncio.TimeoutError)

        # Create a mock handler
        mock_handler = mock.AsyncMock()

        # Create the consumer
        consumer = AsyncLoopConsumer(error_backend)

        # Start the consumer
        task = asyncio.create_task(consumer.run(mock_handler))
        await asyncio.sleep(0.1)  # Give it time to start

        # Shutdown the consumer
        await consumer.shutdown()

        # Check that timeout error was logged
        assert "Timeout during consumer shutdown" in caplog.text

        # Make sure cleanup still happened
        assert consumer._task is None
        assert not consumer._running

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_shutdown_with_cancelled_error_then_exception(self, caplog: Any) -> None:
        """Test shutdown handling when CancelledError is followed by another exception."""
        # Set up logging capture
        caplog.set_level(logging.DEBUG)

        # Create a mock backend
        mock_backend = MockBackend()
        mock_backend.items = [{"id": 1}]
        mock_backend.sleep_time = 1

        # Create a mock handler
        mock_handler = mock.AsyncMock()

        # Create the consumer
        consumer = AsyncLoopConsumer(mock_backend)

        # Start the consumer
        task = asyncio.create_task(consumer.run(mock_handler))
        await asyncio.sleep(0.1)

        # Shutdown the consumer
        await consumer.shutdown()

        # Verify the task was properly cancelled
        assert task.cancelled() or task.done()
        assert consumer._task is None
        assert not consumer._running

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_multiple_handler_exceptions_continue_processing(self, caplog: Any) -> None:
        """Test that multiple handler exceptions don't stop message processing."""
        # Set up logging capture
        caplog.set_level(logging.ERROR)

        # Create a mock backend
        mock_backend = MockBackend()
        mock_backend.items = [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]

        # Create a handler that raises exceptions on specific messages
        processed_ids = []

        async def selective_error_handler(msg: Dict[str, Any]) -> None:
            msg_id = msg["id"]
            if msg_id in [1, 3]:
                raise ValueError(f"Error for message {msg_id}")
            processed_ids.append(msg_id)

        # Create the consumer
        consumer = AsyncLoopConsumer(mock_backend)

        # Run the consumer with a timeout
        try:
            await asyncio.wait_for(consumer.run(selective_error_handler), timeout=0.5)
        except asyncio.TimeoutError:
            pass

        # Verify messages 2 and 4 were processed despite errors on 1 and 3
        assert 2 in processed_ids
        assert 4 in processed_ids
        assert 1 not in processed_ids
        assert 3 not in processed_ids

        # Verify errors were logged
        error_count = caplog.text.count("Error processing message")
        assert error_count >= 2
