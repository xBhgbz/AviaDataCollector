from loguru import logger

from services.consumer import RabbitMQConsumer
from services.handler import DocHandler
from services.main_service import Service
from core.config import neuro_rmq_config
from services.producer import RabbitMQProducer

logger.add("info.log", format="Log: [{time} - {level} - {message}]", level="INFO", enqueue=True)

if __name__ == "__main__":
    doc_handler = DocHandler()
    producer = RabbitMQProducer(neuro_rmq_config)
    consumer = RabbitMQConsumer(neuro_rmq_config, doc_handler, producer)

    service = Service(consumer)
    service.neuro_parse()
