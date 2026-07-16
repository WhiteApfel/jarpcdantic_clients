import pytest
from unittest.mock import AsyncMock, MagicMock

from jarpcdantic_clients import CabbagokServer


class TestCabbagokServer:
    @pytest.mark.asyncio
    async def test_start(self):
        amqp_rpc = AsyncMock()
        amqp_rpc.channel = AsyncMock()
        
        manager = MagicMock()
        manager.handle = "fake_handle"
        
        dispatcher = MagicMock()
        dispatcher.method_map = {"method1": "handler1", "method2": "handler2"}
        manager.dispatcher = dispatcher

        server = CabbagokServer(
            amqp_rpc=amqp_rpc,
            manager=manager,
            queue="test_queue",
            exchange="test_exchange"
        )

        await server.start()

        amqp_rpc.subscribe.assert_awaited_once_with(
            request_handler="fake_handle",
            queue="test_queue",
            exchange="test_exchange",
        )

        assert amqp_rpc.channel.queue_bind.call_count == 2
        amqp_rpc.channel.queue_bind.assert_any_await(
            queue_name="test_queue",
            exchange_name="test_exchange",
            routing_key="method1"
        )
        amqp_rpc.channel.queue_bind.assert_any_await(
            queue_name="test_queue",
            exchange_name="test_exchange",
            routing_key="method2"
        )
