"""
Protocol definitions for queue backends in the MCP server.

This module re-exports the QueueBackendProtocol from abe.types as QueueBackend
for backward compatibility and internal use. All new code should use the types
from abe.types directly.

The centralized type definitions in abe.types ensure consistency across
the entire codebase and plugin ecosystem.
"""

from abe.types import QueueBackendProtocol

# Re-export QueueBackendProtocol as QueueBackend for backward compatibility
# This allows existing internal code to continue using "QueueBackend" while
# the public API uses "QueueBackendProtocol"
QueueBackend = QueueBackendProtocol

__all__ = ["QueueBackend", "QueueBackendProtocol"]
