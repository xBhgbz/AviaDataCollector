import asyncio

from aiormq import AMQPConnectionError
from loguru import logger

from core.config import contract_rmq_config
from services.consumer import NeuroConsumer, SiteConsumer
from services.contact_service import psql_service
from services.producer import AsyncRabbitMQProducer

logger.add("info.log", format="Log: [{time} - {level} - {message}]", level="INFO", enqueue=True)


async def start_service():
    """Запуск консьюмеров сервиса"""

    logger.info("Start Contract service...")

    web_parsing_producer = AsyncRabbitMQProducer(contract_rmq_config)
    neuro_parsing_producer = AsyncRabbitMQProducer(contract_rmq_config)

    parsing_contract_consumer = SiteConsumer(contract_rmq_config, psql_service, web_parsing_producer)
    neuro_contract_consumer = NeuroConsumer(contract_rmq_config, psql_service, neuro_parsing_producer)

    try:
        await parsing_contract_consumer.connect()
        await neuro_contract_consumer.connect()

        async with asyncio.TaskGroup() as tg:
            tasks = [
                tg.create_task(parsing_contract_consumer.consume_messages(contract_rmq_config.RMQ_ROUTING_KEY)),
                tg.create_task(
                    neuro_contract_consumer.consume_messages(contract_rmq_config.NEURO_CONTRACT_RMQ_ROUTING_KEY)
                )
            ]
    except AMQPConnectionError as e:
        logger.error("Ошибка соединения с RabbitMQ: %s" % e)
        raise
    except Exception as e:
        logger.error("Ошибка во время работы сервиса: %s" % e)
        raise
    finally:
        if parsing_contract_consumer.connection:
            await parsing_contract_consumer.connection.close()
        if neuro_contract_consumer.connection:
            await neuro_contract_consumer.connection.close()


if __name__ == "__main__":
    asyncio.run(start_service())
