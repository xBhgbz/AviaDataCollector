import aio_pika
from typing import Protocol, Any

from loguru import logger

from core.config import ContractRabbitMQConfig


class AsyncMQProducer(Protocol):
    """Асинхронный интерфейс для работы с очередью"""

    async def connect(self, url: str):
        """Подключение к продьюсеру"""

    async def publish(self, message: Any):
        """Отправка данных в очередь"""

    async def __aenter__(self):
        """Инициализация контекстного менеджера"""

    async def __aexit__(self):
        """Выход из в контекстном менеджере"""


class AsyncRabbitMQProducer:
    """Асинхронный класс для работы с очередью RabbitMQ"""

    def __init__(self, config: ContractRabbitMQConfig):
        self.config = config
        self.connection: aio_pika.abc.AbstractRobustConnection | None = None
        self.channel: aio_pika.RobustChannel | None = None

    async def connect(self) -> None:
        """Коннекшн к очереди"""
        self.connection: aio_pika.abc.AbstractRobustConnection =\
            await aio_pika.connect_robust(
                host=self.config.RMQ_HOST,
                port=int(self.config.RMQ_PORT),
                login=self.config.RMQ_USER,
                password=self.config.RMQ_PASS
            )

    async def publish(self, message: str) -> None:
        """Асинхронная Отправка данных в очередь"""

        if self.channel and not self.channel.is_closed:
            await self.channel.default_exchange.publish(
                aio_pika.Message(body=message.encode()),
                routing_key=self.config.NEURO_CONTRACT_RMQ_ROUTING_KEY,
            )
        else:
            logger.error("Channel is closed, cannot publish message")

    async def close(self) -> None:
        """Закрытие соединения"""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()

    async def __aenter__(self):
        """Инициализация контекстного менеджера"""
        await self.connect()
        self.channel = await self.connection.channel()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Выход из в контекстном менеджере"""
        if self.channel and not self.channel.is_closed:
            await self.channel.close()
        await self.close()
