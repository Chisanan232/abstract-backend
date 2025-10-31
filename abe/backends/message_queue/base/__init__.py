"""Message-queue backend abstractions."""

from .consumer import EventConsumer
from .protocol import MessageQueueBackend, QueueBackend

__all__ = ["MessageQueueBackend", "EventConsumer", "QueueBackend"]
