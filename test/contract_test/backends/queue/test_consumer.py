import asyncio
from typing import Optional
from unittest import mock

import pytest

from abe.backends.queue.base import QueueBackend
from abe.backends.queue.consumer import AsyncLoopConsumer

from .base.test_consumer_contract import EventConsumerContractTest


class TestAsyncLoopConsumerContract(EventConsumerContractTest):
    """Contract tests for the AsyncLoopConsumer implementation."""

    def create_consumer(self, backend: QueueBackend, group: Optional[str] = None) -> AsyncLoopConsumer:
        """Create a new AsyncLoopConsumer instance for testing."""
        return AsyncLoopConsumer(backend, group=group)

    @pytest.mark.asyncio  # type: ignore[misc]
    async def test_run_idempotence(self, mock_backend: mock.AsyncMock) -> None:
        """Test that calling run multiple times doesn't restart the consumer."""
        # Set up the mock backend
        mock_backend.consume.return_value.__aiter__.return_value = []

        # Create the consumer
        consumer = self.create_consumer(mock_backend)

        # Create a mock handler
        mock_handler = mock.AsyncMock()

        # Call run twice
        task1 = asyncio.create_task(consumer.run(mock_handler))
        await asyncio.sleep(0.05)
        task2 = asyncio.create_task(consumer.run(mock_handler))
        await asyncio.sleep(0.05)

        # Shutdown the consumer
        await consumer.shutdown()

        # Verify consume was only called once
        mock_backend.consume.assert_called_once()
