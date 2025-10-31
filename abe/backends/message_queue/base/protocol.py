"""
Protocol definitions for message-queue backends in the MCP server.

This module re-exports the `MessageQueueBackendProtocol` from `abe.types` as
`MessageQueueBackend`. The legacy alias `QueueBackend` is kept temporarily for
backward compatibility and will be removed in a future major release.
"""

from abe.types import MessageQueueBackendProtocol

# Preferred export name for message-queue backends
MessageQueueBackend = MessageQueueBackendProtocol

__all__ = ["MessageQueueBackend", "MessageQueueBackendProtocol"]
