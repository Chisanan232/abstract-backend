"""Type definitions for the Abstract BackEnd package.

This module provides centralized type aliases and type definitions following
PEP 561, PEP 484, PEP 585, and PEP 695 standards for static type checking with MyPy.

Type aliases use the modern `type` statement (PEP 695) introduced in Python 3.12,
which provides better type inference and cleaner syntax compared to TypeAlias.

Type Hierarchy:
    - JSON types: Basic JSON-compatible types
    - Handler types: Generic handler function signatures
    - Backend types: Generic backend type definitions
    - Protocol types: Abstract backend protocol interfaces
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
    # Handler types
    "HandlerFunc",
    "AsyncHandlerFunc",
    "SyncHandlerFunc",
    "Payload",
    # Backend types
    "BackendKey",
    "BackendPayload",
    "BackendMessage",
    "BackendConfig",
    "ConsumerGroup",
    # Protocol types
    "HandlerProtocol",
    "BackendProtocol",
    # Type guards and validators
    "is_json_serializable",
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
# Handler Type Definitions
# ============================================================================

type Payload = Dict[str, Any]
"""Generic payload data structure for handlers."""

type SyncHandlerFunc = Callable[[Payload], None]
"""Synchronous handler function signature."""

type AsyncHandlerFunc = Callable[[Payload], Awaitable[None]]
"""Asynchronous handler function signature."""

type HandlerFunc = Union[SyncHandlerFunc, AsyncHandlerFunc]
"""Handler function that can be sync or async."""

# ============================================================================
# Backend Type Definitions
# ============================================================================

type BackendKey = str
"""Backend routing key or identifier.

This type represents a key used to route or identify items in a backend.
The interpretation depends on the specific backend implementation.
"""

type BackendPayload = Dict[str, Any]
"""Backend message payload containing the actual data.

This represents the core data being transmitted through the backend.
The payload should be JSON-serializable for compatibility across
different backend implementations.
"""

type BackendMessage = Dict[str, Any]
"""Complete backend message including payload and optional metadata.

This represents the full message structure as consumed from the backend,
which may include the payload along with backend-specific metadata such as
timestamps, message IDs, retry counts, or headers.

The exact structure depends on the backend implementation, but typically
includes at minimum the payload. Backends may add additional fields for
message tracking and processing.
"""

type BackendConfig = Dict[str, str | int | bool]
"""Configuration dictionary for backend initialization.

This type represents configuration options passed to backends, typically
loaded from environment variables. The exact keys and values depend on the
specific backend implementation.
"""

type ConsumerGroup = str | None
"""Consumer group identifier for group-based consumption patterns.

Consumer groups enable multiple consumers to work together to process messages,
with each message being delivered to only one consumer in the group.
This is useful for load balancing and parallel processing.

- If None: Consumer operates independently (no group coordination)
- If str: Consumer joins the specified group for coordinated consumption
"""

# ============================================================================
# Protocol Definitions (PEP 544)
# ============================================================================


@runtime_checkable
class HandlerProtocol(Protocol):
    """Protocol for objects that can handle payloads.

    This protocol defines the interface that all handlers must implement.
    It follows PEP 544 for structural subtyping.
    """

    async def handle(self, payload: Payload) -> None:
        """Handle a payload.

        Args:
            payload: The payload to process
        """
        ...


@runtime_checkable
class BackendProtocol(Protocol):
    """Protocol for backend implementations.

    This protocol defines the interface that all backends must implement
    for publishing and consuming messages. It follows PEP 544 for structural
    subtyping, enabling plugin-based backend implementations.

    All backend plugins should implement this protocol to ensure
    compatibility with the system. The protocol uses type aliases
    defined in this module for consistency across all implementations.

    Plugin Architecture:
        Backends are discovered via Python entry points in the
        'abe.backends' group. Plugins should:

        1. Implement this protocol
        2. Use the type aliases from abe.types
        3. Register via entry points in pyproject.toml
        4. Provide a from_env() class method for configuration
    """

    async def publish(self, key: BackendKey, payload: BackendPayload) -> None:
        """Publish a message to the backend.

        Args:
            key: The routing key or identifier for the message
            payload: The message payload as a dictionary
        """
        ...

    async def consume(self, *, group: ConsumerGroup = None) -> AsyncIterator[BackendMessage]:
        """Consume messages from the backend.

        This method returns an async iterator that yields messages from the backend.
        It should run indefinitely, yielding messages as they become available.

        Args:
            group: Optional consumer group identifier for coordinated consumption

        Yields:
            BackendMessage: Messages from the backend
        """
        yield {}

    @classmethod
    def from_env(cls) -> BackendProtocol:
        """Create a backend instance from environment variables.

        This factory method creates and configures a backend instance
        using configuration from environment variables.

        Returns:
            BackendProtocol: A configured instance of the backend
        """
        ...


# ============================================================================
# Type Guards and Validators
# ============================================================================


def is_json_serializable(value: Any) -> bool:
    """Type guard to check if a value is JSON-serializable.

    Validates that the value can be safely serialized to JSON format.
    Supports all JSON-compatible types: primitives, dicts, and lists.

    Args:
        value: The value to check

    Returns:
        True if the value is JSON-serializable
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return True

    if isinstance(value, dict):
        return all(isinstance(k, str) and is_json_serializable(v) for k, v in value.items())

    if isinstance(value, (list, tuple)):
        return all(is_json_serializable(item) for item in value)

    return False
