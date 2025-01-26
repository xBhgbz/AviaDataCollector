import json
import time
from typing import Protocol

import pika

from loguru import logger

from core.config import NeuroRabbitMQConfig
from services.handler import BaseDocHandler
from services.neuro import NeuroDuckDuckGo
from services.producer import MQProducer


class MQConsumer(Protocol):
    """Интерфейс консьюмера"""

    def connect(self):
        """Установка соединения"""

    def process_new_message(self, channel, method, properties, body: bytes):
        """Обработка сообщения"""

    def consume_messages(self, channel):
        """Цикл принятия сообщений"""


class RabbitMQConsumer:
    """Класс для работы с RabbitMQ"""

    def __init__(
            self,
            config: NeuroRabbitMQConfig,
            doc_handler: BaseDocHandler,
            producer: MQProducer
    ):
        self.config = config
        self.doc_handler = doc_handler
        self.producer = producer

    def connect(self) -> pika.BlockingConnection:
        """Установка соединения"""
        connection_params = pika.ConnectionParameters(
            host=self.config.RMQ_HOST,
            port=self.config.RMQ_PORT,
            credentials=pika.PlainCredentials(self.config.RMQ_USER, self.config.RMQ_PASS)
        )
        return pika.BlockingConnection(
            parameters=connection_params
        )

    def process_new_message(self, channel, method, properties, body: bytes) -> None:
        """Обработка сообщения"""

        logger.info('Raw body: %s' % body)
        received: dict = json.loads(body.decode("utf-8"))
        site_url, tender_number, documents_info = received["site_url"], received["tender_number"], received["documents_info"]
        logger.info("Received message %s %s %s" % (site_url, tender_number, documents_info))

        is_large_doc = False

        try:
            self.doc_handler.process_document(documents_info["link"], documents_info["title"], documents_info["extension"])
        except IOError:
            is_large_doc = True
            logger.info("Размер файла превышает заданный лимит! Подтвердили сообщение")
        while True:
            logger.info("Start parsing cycle...")
            response = {"avia_data": None}
            try:
                logger.info("start neuro chat: consumer")
                if not is_large_doc:
                    neuro = NeuroDuckDuckGo()
                    response: dict = neuro.neuro_chat()
            except RuntimeError:
                logger.error("Runtime error in consumer!")
                time.sleep(60 * 30)
            except Exception as e:
                logger.error(f"НЕ УДАЛОСЬ ПООБЩАТЬСЯ С НЕЙРОНКОЙ по причине: {e}")
            else:
                logger.info("Message from neuro-chat: %s" % response)
                message = {"parsed_data": response, "site_url": site_url, "tender_number": tender_number}
                with self.producer.connect() as connection:
                    logger.info("Connected to RabbitMQ (producer)...")
                    with connection.channel() as producer_channel:
                        logger.info("Publishing batch message...")
                        self.producer.publish(channel=producer_channel, message=message)
                channel.basic_ack(delivery_tag=method.delivery_tag)
                break

    def consume_messages(self, channel):
        """Цикл принятия сообщений"""
        channel.basic_qos(prefetch_count=1)
        channel.queue_declare(queue=self.config.NEURO_CONTRACT_RMQ_ROUTING_KEY)

        channel.basic_consume(
            queue=self.config.NEURO_CONTRACT_RMQ_ROUTING_KEY,
            on_message_callback=self.process_new_message,
            # auto_ack=True,
        )
        logger.warning("Waiting for messages...")
        channel.start_consuming()
