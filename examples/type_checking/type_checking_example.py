"""
Example demonstrating type checking with the abstract-backend package.

This example shows how to use the types module for static type checking
with MyPy and other type checkers.

Run MyPy on this file to verify type checking:
    uv run mypy examples/type_checking/type_checking_example.py
"""

from __future__ import annotations

from typing import Any

from abe.types import (
    AsyncEventHandlerFunc,
    ConsumerGroup,
    EventHandlerFunc,
    EventHandlerProtocol,
    QueueBackendProtocol,
    QueueKey,
    QueueMessage,
    QueuePayload,
    SyncEventHandlerFunc,
    WebhookEventPayload,
)


# Example 1: Event handler implementation
class EventHandler:
    """Example event handler implementing EventHandlerProtocol."""

    async def handle_event(self, event: WebhookEventPayload) -> None:
        """Handle a webhook event.

        Args:
            event: The webhook event payload
        """
        print(f"Processing event: {event}")


# Example 2: Event handler functions
def sync_handler(event: WebhookEventPayload) -> None:
    """Synchronous event handler.

    Args:
        event: The webhook event payload
    """
    print(f"Sync handler: {event}")


async def async_handler(event: WebhookEventPayload) -> None:
    """Asynchronous event handler.

    Args:
        event: The webhook event payload
    """
    print(f"Async handler: {event}")


# Example 3: Queue backend implementation
class SimpleQueueBackend(QueueBackendProtocol):
    """Example queue backend implementing QueueBackendProtocol."""

    async def publish(self, key: QueueKey, payload: QueuePayload) -> None:
        """Publish a message to the queue.

        Args:
            key: The routing key
            payload: The message payload
        """
        print(f"Publishing to {key}: {payload}")

    async def consume(self, *, group: ConsumerGroup = None) -> Any:
        """Consume messages from the queue.

        Args:
            group: Optional consumer group

        Yields:
            Messages from the queue
        """
        yield {"type": "message", "data": "example"}

    @classmethod
    def from_env(cls) -> SimpleQueueBackend:
        """Create backend from environment.

        Returns:
            Configured backend instance
        """
        return cls()


# Main demonstration
def main() -> None:
    """Demonstrate type checking features."""
    print("=== Type Checking Examples ===\n")

    # Example 1: Event handler with protocol compliance
    handler: EventHandlerProtocol = EventHandler()
    print("✓ Event handler implements EventHandlerProtocol")

    # Example 2: Event handler functions
    sync_func: SyncEventHandlerFunc = sync_handler
    async_func: AsyncEventHandlerFunc = async_handler
    combined_func: EventHandlerFunc = sync_handler
    print("✓ Event handler functions type-checked")

    # Example 3: Queue backend with protocol compliance
    backend: QueueBackendProtocol = SimpleQueueBackend()
    print("✓ Queue backend implements QueueBackendProtocol")

    # Example 4: Type aliases in use
    key: QueueKey = "events"
    payload: QueuePayload = {"type": "message", "text": "Hello"}
    group: ConsumerGroup = "processors"
    message: QueueMessage = {"id": "msg-1", "data": "example"}
    print(f"✓ Using type aliases: key={key}, group={group}")

    print("\n✓ All type checking examples completed successfully!")


if __name__ == "__main__":
    main()
