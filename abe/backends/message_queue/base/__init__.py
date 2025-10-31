"""Message-queue backend abstractions."""

from .consumer import EventConsumer
from .protocol import MessageQueueBackend

__all__ = ["MessageQueueBackend", "EventConsumer"]
