# -*- coding: utf-8 -*-
import asyncio
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cabbagok import AsyncAmqpRpc
    from jarpcdantic import AsyncJarpcManager


class CabbagokServer:
    """
    Утилитный класс для быстрого старта RPC-сервера поверх Cabbagok.
    """

    def __init__(
        self,
        amqp_rpc: "AsyncAmqpRpc",
        manager: "AsyncJarpcManager",
        queue: str,
        exchange: str,
    ):
        """
        :param amqp_rpc: Cabbagok RPC object.
        :param manager: AsyncJarpcManager object.
        :param queue: Name of the queue to subscribe to.
        :param exchange: Name of the exchange to bind to.
        """
        self.amqp_rpc = amqp_rpc
        self.manager = manager
        self.queue = queue
        self.exchange = exchange

    async def start(self) -> None:
        """
        Подписывается на очередь и биндит все методы из диспетчера в exchange.
        """
        await self.amqp_rpc.subscribe(
            request_handler=self.manager.handle,
            queue=self.queue,
            exchange=self.exchange,
        )

        tasks = [
            self.amqp_rpc.channel.queue_bind(
                queue_name=self.queue,
                exchange_name=self.exchange,
                routing_key=method,
            )
            for method in self.manager.dispatcher.method_map
        ]

        if tasks:
            await asyncio.gather(*tasks)
