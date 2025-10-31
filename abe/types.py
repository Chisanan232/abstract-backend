"""
Type definitions for the Abstract BackEnd package.

This module provides centralized type aliases and type definitions following
PEP 561, PEP 484, PEP 585, and PEP 695 standards for static type checking with MyPy.

Type aliases use the modern `type` statement (PEP 695) introduced in Python 3.12,
which provides better type inference and cleaner syntax compared to TypeAlias.

Type Hierarchy:
    - JSON types: Basic JSON-compatible types
    - Event types: Event handling type definitions
    - Handler types: Handler function signatures
"""

from __future__ import annotations

from typing import (
    Any,
    AsyncIterator,
    Awaitable,
    Callable,
    Dict,
    List,
    Protocol,
    Union,
    runtime_checkable,
)

__all__ = [
    # JSON types
    "JSONValue",
    "JSONDict",
    "JSONList",
    "JSONPrimitive",
    "WebhookEventPayload",
    # Handler types
    "EventHandlerFunc",
    "AsyncEventHandlerFunc",
    "SyncEventHandlerFunc",
    # Message queue types
    "MessageQueueKey",
    "MessageQueuePayload",
    "MessageQueueMessage",
    "MessageQueueBackendConfig",
    "ConsumerGroup",
    # Protocol types
    "EventHandlerProtocol",
    "MessageQueueBackendProtocol",
]

# ============================================================================
# JSON Type Definitions (PEP 484/585/695)
# ============================================================================

type JSONPrimitive = Union[str, int, float, bool, None]
"""Primitive JSON-compatible types."""

type JSONValue = Union[JSONPrimitive, JSONDict, JSONList]
"""Any valid JSON value type."""

type JSONDict = Dict[str, JSONValue]
"""JSON object represented as a dictionary."""

type JSONList = List[JSONValue]
"""JSON array represented as a list."""

# ============================================================================
# Webhook event Type Definitions
# ============================================================================

type WebhookEventPayload = Dict[str, Any]
"""Webhook event payload as received from the Events API."""

# ============================================================================
# Event Handler Type Definitions
# ============================================================================

type SyncEventHandlerFunc = Callable[[WebhookEventPayload], None]
"""Synchronous event handler function signature."""

type AsyncEventHandlerFunc = Callable[[WebhookEventPayload], Awaitable[None]]
"""Asynchronous event handler function signature."""

type EventHandlerFunc = Union[SyncEventHandlerFunc, AsyncEventHandlerFunc]
"""Event handler function that can be sync or async."""

# ============================================================================
# Message Queue Type Definitions
# ============================================================================

type MessageQueueKey = str
"""Message-queue routing key or topic name.

This type represents the routing key or topic used to publish and route
messages in message-queue backends. Different backends may use this differently:
- Kafka: Topic name
- Redis Streams: Stream key
- RabbitMQ: Routing key
- Memory: Simple key for routing

Examples:
    >>> # Slack events topic
    >>> key: MessageQueueKey = "slack_events"
    >>>
    >>> # Channel-specific routing
    >>> channel_id = "C1234567890"
    >>> key: MessageQueueKey = f"slack.channel.{channel_id}"
    >>>
    >>> # Event type routing
    >>> key: MessageQueueKey = "slack.events.message"
"""

type MessageQueuePayload = Dict[str, Any]
"""Message-queue payload containing the actual data.

This represents the core data transmitted through the message queue, typically
a Slack event payload or other structured data. The payload should be
JSON-serializable for compatibility across different message-queue backends.

Examples:
    >>> # Slack event payload
    >>> payload: MessageQueuePayload = {
    ...     "type": "message",
    ...     "channel": "C1234567890",
    ...     "user": "U1234567890",
    ...     "text": "Hello, world!",
    ...     "ts": "1234567890.123456"
    ... }
    >>>
    >>> # Custom application payload
    >>> payload: MessageQueuePayload = {
    ...     "event_type": "user_action",
    ...     "data": {"action": "click", "target": "button"}
    ... }
"""

type MessageQueueMessage = Dict[str, Any]
"""Complete message-queue message including payload and optional metadata.

This represents the full message structure as consumed from the message queue,
which may include the payload along with backend-specific metadata such as
timestamps, message IDs, retry counts, or headers.

The exact structure depends on the backend implementation, but typically
includes at minimum the payload. Backends may add additional fields for message
tracking and processing.

Examples:
    >>> # Simple message (memory backend)
    >>> message: MessageQueueMessage = {
    ...     "type": "message",
    ...     "channel": "C1234567890",
    ...     "text": "Hello"
    ... }
    >>>
    >>> # Message with metadata (Redis/Kafka backend)
    >>> message: MessageQueueMessage = {
    ...     "payload": {
    ...         "type": "message",
    ...         "channel": "C1234567890",
    ...         "text": "Hello"
    ...     },
    ...     "metadata": {
    ...         "message_id": "msg-123",
    ...         "timestamp": 1234567890.123,
    ...         "retry_count": 0
    ...     }
    ... }

Note:
    Plugin implementations should document their specific message structure to
    help consumers understand what fields are available.
"""

type MessageQueueBackendConfig = Dict[str, str | int | bool]
"""Configuration dictionary for message-queue backend initialization.

This type represents configuration options passed to message-queue backends,
typically loaded from environment variables. The exact keys and values depend
on the specific backend implementation.

Examples:
    >>> # Redis backend configuration
    >>> config: MessageQueueBackendConfig = {
    ...     "url": "redis://localhost:6379",
    ...     "max_connections": 10,
    ...     "decode_responses": True
    ... }
    >>>
    >>> # Kafka backend configuration
    >>> config: MessageQueueBackendConfig = {
    ...     "bootstrap_servers": "localhost:9092",
    ...     "group_id": "slack-consumers",
    ...     "auto_offset_reset": "earliest"
    ... }
"""

type ConsumerGroup = str | None
"""Consumer group identifier for group-based consumption patterns.

Consumer groups enable multiple consumers to work together to process messages
from a queue, with each message being delivered to only one consumer in the group.
This is useful for load balancing and parallel processing.

- If None: Consumer operates independently (no group coordination)
- If str: Consumer joins the specified group for coordinated consumption

Examples:
    >>> # Independent consumer (no group)
    >>> group: ConsumerGroup = None
    >>>
    >>> # Consumer group for load balancing
    >>> group: ConsumerGroup = "slack-event-processors"
    >>>
    >>> # Environment-specific consumer group
    >>> import os
    >>> group: ConsumerGroup = f"slack-consumers-{os.getenv('ENV', 'dev')}"

Note:
    Not all queue backends support consumer groups. The memory backend
    ignores this parameter, while Redis Streams and Kafka use it for
    coordinated consumption.
"""

# ============================================================================
# Protocol Definitions (PEP 544)
# ============================================================================


@runtime_checkable
class EventHandlerProtocol(Protocol):
    """Protocol for objects that can handle Slack events.

    This protocol defines the interface that all event handlers must implement.
    It follows PEP 544 for structural subtyping.

    Example:
        >>> class MyHandler:
        ...     async def handle_event(self, event: Dict[str, Any]) -> None:
        ...         print(f"Handling event: {event['type']}")
        >>>
        >>> handler: EventHandlerProtocol = MyHandler()
    """

    async def handle_event(self, event: WebhookEventPayload) -> None:
        """Handle a Slack event.

        Args:
            event: The Slack event payload
        """
        ...


@runtime_checkable
class MessageQueueBackendProtocol(Protocol):
    """Protocol for message-queue backend implementations.

    This protocol defines the interface that all message-queue backends must
    implement for publishing and consuming messages. It follows PEP 544 for
    structural subtyping, enabling plugin-based backend implementations.

    All message-queue backend plugins should implement this protocol to ensure
    compatibility with the abstract backend. The protocol uses type aliases
    defined in this module for consistency across all implementations.

    Plugin Architecture:
        Message-queue backends are discovered via Python entry points in the
        'slack_mcp.backends.message_queue' group. Plugins should:

        1. Implement this protocol
        2. Use the type aliases from slack_mcp.types
        3. Register via entry points in pyproject.toml
        4. Provide a from_env() class method for configuration

    Example Implementation:
        >>> from abe.types import (
        ...     MessageQueueBackendProtocol,
        ...     MessageQueueKey,
        ...     MessageQueuePayload,
        ...     MessageQueueMessage,
        ...     ConsumerGroup,
        ... )
        >>> from typing import AsyncIterator
        >>>
        >>> class RedisBackend:
        ...     '''Redis implementation of a message-queue backend.'''
        ...
        ...     async def publish(
        ...         self,
        ...         key: MessageQueueKey,
        ...         payload: MessageQueuePayload,
        ...     ) -> None:
        ...         # Publish to Redis stream
        ...         pass
        ...
        ...     async def consume(
        ...         self,
        ...         *,
        ...         group: ConsumerGroup = None,
        ...     ) -> AsyncIterator[MessageQueueMessage]:
        ...         # Consume from Redis stream
        ...         yield {}
        ...
        ...     @classmethod
        ...     def from_env(cls) -> "RedisBackend":
        ...         # Load config from environment
        ...         return cls()
        >>>
        >>> # Type checker validates protocol compliance
        >>> backend: MessageQueueBackendProtocol = RedisBackend()

    Entry Point Registration:
        In your plugin's pyproject.toml:

        [project.entry-points."slack_mcp.backends.message_queue"]
        redis = "slack_mcp_mq_redis:RedisBackend"

    See Also:
        - MessageQueueKey: Type alias for routing keys
        - MessageQueuePayload: Type alias for message payloads
        - MessageQueueMessage: Type alias for consumed messages
        - ConsumerGroup: Type alias for consumer group identifiers
    """

    async def publish(self, key: MessageQueueKey, payload: MessageQueuePayload) -> None:
        """Publish a message to the message queue.

        This method publishes a message to the backend using the specified
        routing key. The payload must be JSON-serializable for compatibility
        across different message-queue backends.

        Args:
            key: The routing key or topic for the message. Used to route messages
                to appropriate consumers or partitions.
            payload: The message payload as a dictionary. Should contain
                JSON-serializable data.

        Raises:
            Exception: Implementation-specific exceptions for connection errors,
                serialization failures, or other publishing issues.

        Example:
            >>> backend = RedisBackend.from_env()
            >>> await backend.publish(
            ...     key="slack_events",
            ...     payload={"type": "message", "text": "Hello"}
            ... )
        """
        ...

    async def consume(
        self,
        *,
        group: ConsumerGroup = None,
    ) -> AsyncIterator[MessageQueueMessage]:
        """Consume messages from the message queue.

        This method returns an async iterator that yields messages from the
        queue. It should run indefinitely, yielding messages as they become
        available.

        Consumer groups enable multiple consumers to process messages together,
        with each message delivered to only one consumer in the group. Not all
        backends support consumer groups—implementations should document their
        behavior when groups are not supported.

        Args:
            group: Optional consumer group identifier for coordinated consumption.
                - If None: Consumer operates independently
                - If str: Consumer joins the specified group
                Backends that don't support groups should ignore this parameter.

        Yields:
            MessageQueueMessage: Messages from the message queue. The structure
                may vary by backend but should at minimum contain the payload
                data.

        Raises:
            Exception: Implementation-specific exceptions for connection errors,
                deserialization failures, or other consumption issues.

        Example:
            >>> backend = RedisBackend.from_env()
            >>> async for message in backend.consume(group="processors"):
            ...     event_type = message.get("type")
            ...     print(f"Processing {event_type}")

        Note:
            Implementations should handle cancellation gracefully and clean up
            resources when the async iterator is closed.
        """
        yield {}

    @classmethod
    def from_env(cls) -> "MessageQueueBackendProtocol":
        """Create a backend instance from environment variables.

        This factory method creates and configures a message-queue backend
        instance using configuration from environment variables. Each backend
        implementation defines its own required environment variables.

        The method should:
        1. Read configuration from environment variables
        2. Validate required configuration is present
        3. Create and return a configured backend instance
        4. Raise clear errors if configuration is invalid

        Returns:
            MessageQueueBackendProtocol: A configured instance of the backend
                ready for use.

        Raises:
            ValueError: If required environment variables are missing or invalid.
            Exception: Implementation-specific configuration errors.

        Example:
            >>> # Redis backend expects REDIS_URL
            >>> import os
            >>> os.environ["REDIS_URL"] = "redis://localhost:6379"
            >>> backend = RedisBackend.from_env()
            >>>
            >>> # Kafka backend expects KAFKA_BOOTSTRAP_SERVERS
            >>> os.environ["KAFKA_BOOTSTRAP_SERVERS"] = "localhost:9092"
            >>> backend = KafkaBackend.from_env()

        Note:
            Plugin implementations should document their required environment
            variables and provide sensible defaults where appropriate.
        """
        ...
