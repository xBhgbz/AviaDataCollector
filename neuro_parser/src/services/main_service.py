from loguru import logger

from services.consumer import MQConsumer
from services.handler import BaseDocHandler
from services.neuro import BaseNeuroStream
from services.producer import MQProducer


class Service:

    def __init__(
            self,
            consumer: MQConsumer,
    ):
        self.consumer = consumer

    def neuro_parse(self):
        """Запускает основной процесс обработки тендеров нейросетью"""
        logger.info("Starting neuro-parse...")
        with self.consumer.connect() as connection:
            logger.info("Connection open.")
            with connection.channel() as channel:
                self.consumer.consume_messages(channel)




