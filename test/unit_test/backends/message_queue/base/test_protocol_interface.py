"""
Unit tests for the MessageQueueBackend protocol interface.

These tests verify the structural aspects of the protocol definition itself,
ensuring that the required methods and signatures are correctly defined.
Protocol methods with ellipsis (...) placeholders are excluded from coverage
reporting via .coveragerc configuration.
"""

from abe.backends.message_queue.base import MessageQueueBackend


class TestMessageQueueBackendInterface:
    """Tests focused on the MessageQueueBackend protocol interface structure."""

    def test_protocol_definition(self) -> None:
        """Verify the protocol interface is correctly defined with required methods.

        This test checks that:
        1. The protocol methods contain appropriate placeholder implementations
        2. All required methods (publish, consume) exist
        3. The classmethod from_env is properly defined

        Protocol methods with placeholders are properly excluded from coverage
        requirements via the .coveragerc configuration, as they are interface
        definitions rather than executable code.
        """
        from inspect import getsource

        # Get the source code of the protocol methods
        publish_source = getsource(MessageQueueBackend.publish)
        consume_source = getsource(MessageQueueBackend.consume)

        # Verify method bodies contain appropriate placeholders for Protocol interface definitions
        assert "..." in publish_source, "publish method should have ellipsis placeholder"
        # consume now uses a yield statement instead of ellipsis for proper AsyncIterator typing
        assert "yield" in consume_source, "consume method should have a yield statement placeholder"

        # Verify from_env exists as a classmethod on the protocol
        assert hasattr(MessageQueueBackend, "from_env"), "from_env classmethod should exist on the protocol"

        # Verify the expected method names exist on the protocol
        expected_methods = {"publish", "consume"}
        protocol_methods = {
            name for name in dir(MessageQueueBackend) if not name.startswith("_") and name not in {"from_env"}
        }
        assert expected_methods == protocol_methods, (
            f"MessageQueueBackend protocol should define these methods: {expected_methods}, "
            f"but it defines: {protocol_methods}"
        )
