"""
Abstract consumer protocol for processing message-queue messages.

This module defines the EventConsumer protocol that specifies the interface
for consuming and processing messages from message-queue backends.
"""

import logging
from typing import Any, Awaitable, Callable, Dict, Protocol

# Set up logger for this module
logger = logging.getLogger(__name__)


class EventConsumer(Protocol):
    """Protocol defining the interface for event consumers.

    An event consumer is responsible for processing messages from a
    message-queue backend and passing them to a handler function.
    """

    async def run(self, handler: Callable[[Dict[str, Any]], Awaitable[None]]) -> None:
        """Run the consumer, processing messages with the given handler.

        Args:
            handler: An async function that will be called with each message payload
        """
        ...

    async def shutdown(self) -> None:
        """Gracefully stop the consumer.

        This method should ensure that any in flight messages are processed
        before the consumer stops.
        """
        ...
