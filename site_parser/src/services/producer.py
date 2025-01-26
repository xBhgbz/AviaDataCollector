import json
from typing import Protocol, Any

import pika

from core.config import RabbitMQConfig
from tools import backoff


class MQProducer(Protocol):

    def connect(self):
        """Подключение к продьюсеру"""

    def publish(self, channel, message: Any):
        """Отправка данных в очередь"""

    def batch_publish(self, channel, data: list, batch: int):
        """Отправка данных в очередь по батчам"""


class RabbitMQProducer:

    def __init__(self, config: RabbitMQConfig):
        self.config = config

    @backoff()
    def connect(self) -> pika.BlockingConnection:
        connection_params = pika.ConnectionParameters(
            host=self.config.RMQ_HOST,
            port=self.config.RMQ_PORT,
            credentials=pika.PlainCredentials(self.config.RMQ_USER, self.config.RMQ_PASS)
        )
        return pika.BlockingConnection(
            parameters=connection_params
        )

    def publish(self, channel, message: dict[str, Any]) -> None:
        """Отправка данных в очередь"""
        channel.queue_declare(queue=self.config.RMQ_ROUTING_KEY)
        channel.basic_publish(
            exchange=self.config.RMQ_EXCHANGE,
            routing_key=self.config.RMQ_ROUTING_KEY,
            body=message
        )

    @backoff()
    def batch_publish(self, channel, data: list, batch: int | None = None) -> None:
        """Отправка данных в очередь по батчам"""

        channel.queue_declare(queue=self.config.RMQ_ROUTING_KEY)
        batch = batch or int(self.config.BATCH_SIZE)

        for i in range(0, len(data), batch):
            message = data[i:i+batch]
            channel.basic_publish(
                exchange=self.config.RMQ_EXCHANGE,
                routing_key=self.config.RMQ_ROUTING_KEY,
                body=json.dumps(message)
            )

