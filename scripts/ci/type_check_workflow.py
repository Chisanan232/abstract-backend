"""Utility tasks for type-check CI workflow.

Each task mirrors a python snippet formerly embedded in
`.github/workflows/type-check.yml`, enabling easier maintenance.
"""

from __future__ import annotations

import argparse


def import_types_module() -> None:
    """Import `abe.types` module and report export count."""

    from abe import types  # noqa: WPS433 (import within function for CLI task)

    print("✅ Successfully imported types module")
    print(f"✅ Available types: {len(types.__all__)} exports")


def import_core_types() -> None:
    """Import core type exports to ensure availability."""

    from abe.types import (  # noqa: WPS433 (import within function)
        EventHandlerProtocol,
        MessageQueueBackendProtocol,
        WebhookEventPayload,
    )

    # Reference imports to satisfy linters.
    _ = (WebhookEventPayload, EventHandlerProtocol, MessageQueueBackendProtocol)

    print("✅ Successfully imported core types")
    print("✅ WebhookEventPayload, EventHandlerProtocol, MessageQueueBackendProtocol available")


def verify_type_attributes() -> None:
    """Assert expected attributes exist on `abe.types`."""

    from abe import types  # noqa: WPS433

    # JSON types
    for attr in ("JSONValue", "JSONDict", "JSONList", "JSONPrimitive"):
        assert hasattr(types, attr), f"Missing {attr}"
    print("✅ JSON types accessible")

    # Event types
    assert hasattr(types, "WebhookEventPayload"), "Missing WebhookEventPayload"
    print("✅ Event types accessible")

    # Handler types
    for attr in ("EventHandlerFunc", "AsyncEventHandlerFunc", "SyncEventHandlerFunc"):
        assert hasattr(types, attr), f"Missing {attr}"
    print("✅ Handler types accessible")

    # Message queue types
    for attr in (
        "MessageQueueKey",
        "MessageQueuePayload",
        "MessageQueueMessage",
        "MessageQueueBackendConfig",
        "ConsumerGroup",
    ):
        assert hasattr(types, attr), f"Missing {attr}"
    print("✅ Message queue types accessible")

    # Protocol types
    for attr in ("EventHandlerProtocol", "MessageQueueBackendProtocol"):
        assert hasattr(types, attr), f"Missing {attr}"
    print("✅ Protocol types accessible")


def verify_protocol_implementations() -> None:
    """Validate protocol structure expectations."""

    from abe.types import (  # noqa: WPS433
        EventHandlerProtocol,
        MessageQueueBackendProtocol,
    )

    assert hasattr(EventHandlerProtocol, "handle_event"), "handle_event missing"
    print("✅ EventHandlerProtocol has handle_event method")

    for attr in ("publish", "consume", "from_env"):
        assert hasattr(MessageQueueBackendProtocol, attr), f"{attr} missing"
    print("✅ MessageQueueBackendProtocol has all required methods")

    print("✅ Protocol implementations verified")


TASKS = {
    "module": import_types_module,
    "core": import_core_types,
    "attributes": verify_type_attributes,
    "protocols": verify_protocol_implementations,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run type-related verification tasks used by CI workflow.",
    )
    parser.add_argument(
        "task",
        choices=TASKS,
        help="Task identifier to execute",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    TASKS[args.task]()


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()
