import json

import aio_pika

from typing import Protocol

import aiohttp
from loguru import logger
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from contstants import EXTENSIONS
from services.request_builder import build_json_for_avia_admin
from core.config import ContractRabbitMQConfig
from services.contact_service import DBService

from schemas.entity import ContractDataModel, GetFieldContractData, ContractForAdminModel
from services.producer import AsyncRabbitMQProducer


class AsyncMQConsumer(Protocol):
    """Асинхронный Интерфейс консьюмера"""

    async def connect(self, url: str):
        """Установка соединения"""

    async def process_new_message(self, message):
        """Обработка сообщения"""

    async def consume_messages(self):
        """Цикл принятия сообщений"""


class RabbitMQConsumer:
    """Асинхронный класс для работы с RabbitMQ"""

    def __init__(self, config):
        self.config = config
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.RobustChannel | None = None

    async def connect(self) -> None:
        """Установка соединения"""

        self.connection = await aio_pika.connect_robust(
            host=self.config.RMQ_HOST,
            port=int(self.config.RMQ_PORT),
            login=self.config.RMQ_USER,
            password=self.config.RMQ_PASS
        )
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)

    async def process_new_message(self, message) -> None:
        """Обработка сообщения"""

    async def consume_messages(self, routing_key: str):
        """Цикл принятия сообщений"""

        logger.info("Consuming messages... %s" % routing_key)

        if not self.channel:
            raise ConnectionError("Consumer is not connected to RabbitMQ")

        queue = await self.channel.declare_queue(name=routing_key)

        logger.warning("Waiting for messages...")

        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                logger.info("Process messages...")
                await self.process_new_message(message)
        # await queue.consume(callback=self.process_new_message)


class NeuroConsumer(RabbitMQConsumer):
    """Консьюмер для сервиса нейро-парсинга"""

    def __init__(self, config: ContractRabbitMQConfig, db_service: DBService, producer: AsyncRabbitMQProducer):
        super().__init__(config)
        self.producer = producer
        self.db_service = db_service

    async def consume_messages(self, routing_key: str = ""):
        await super().consume_messages(self.config.NEURO_CONTRACT_RESPONSE_RMQ_ROUTING_KEY)

    async def process_new_message(self, message) -> None:
        """Обработка сообщения для сервиса нейро-парсинга"""

        logger.info("Process message... %s, type: %s" % (message.body, type(message.body)))
        async with message.process():
            receive_message = message.body.decode()
            receive_message = json.loads(receive_message)

            logger.info("Received message from neuro-parser: %s" % receive_message)

            contact_id = GetFieldContractData(
                tender_number=receive_message["tender_number"],
                site_url=receive_message["site_url"]
            )

            amount = await self.db_service.get_field(
                contact_id,
                "amount_parsed_files"
            )
            amount += 1  # раз мы тут мы уже обработали файл
            logger.info("Amount: %d" % amount)

            try:
                documents_info = await self.db_service.get_field(
                    contact_id,
                    "documents_info"
                )
            except Exception as e:
                logger.error("EXCEPT %s" % e)
                raise

            try:
                await self.db_service.update(
                    data=contact_id,
                    update_values={"amount_parsed_files": amount}
                )
            except SQLAlchemyError as e:
                logger.error("Ошибка при записи в базу данных: %s" % e)
            except Exception as e:
                logger.error("Общая ошибка при записи в базу данных %s" % e)

            avia_data: dict = receive_message.get("parsed_data", {}).get("avia_data", None)
            contract_data: dict = receive_message.get("parsed_data", {}).get("contract_data", None)

            if avia_data:
                logger.info("Avia-data find! Sending in django...")
                try:
                    contact_info: ContractForAdminModel = await self.db_service.get_contract_data(
                        data=contact_id,
                    )
                except SQLAlchemyError as e:
                    logger.error("Ошибка при получении информации о контракте %s" % e)
                except Exception as e:
                    logger.error("Общая ошибка при получении информации о контракте %s" % e)

                message: dict = build_json_for_avia_admin(contract_data, avia_data, contact_info)

                dump_message = json.dumps(message)
                logger.info("DUMP: %s" % dump_message)

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                            "http://admin:8000/api/contract/",
                            data=json.dumps(message),
                            headers={"Content-Type": "application/json"}
                    ) as response:
                        logger.warning("Status: %s" % response.status)
                logger.info("Success!")

            else:
                if len(documents_info) == amount:
                    # все спарсили
                    # TODO проставить finished_at или статус
                    logger.warning("Files ended...")

                    pass
                else:
                    logger.info("Sending producer... Again!")
                    async with self.producer as prdr:
                        next_data = {
                            "site_url": receive_message["site_url"],
                            "tender_number": receive_message["tender_number"],
                            "documents_info": documents_info[amount]
                        }
                        await prdr.publish(message=json.dumps(next_data))


class SiteConsumer(RabbitMQConsumer):
    """Консьюмер для сервиса веб-парсинга"""

    def __init__(self, config: ContractRabbitMQConfig, db_service: DBService, producer: AsyncRabbitMQProducer):
        super().__init__(config)
        self.producer = producer
        self.db_service = db_service

    async def consume_messages(self, routing_key: str = ""):
        await super().consume_messages(self.config.RMQ_ROUTING_KEY)

    async def process_new_message(self, message) -> None:
        """Обработка сообщения для сервиса веб-парсинга"""

        logger.info("Start proccess...")

        async with message.process():
            messages: dict = json.loads(message.body.decode())

            for received_message in messages:
                logger.info("Message: %s" % received_message)
                result: list = []

                if len(received_message["documents_info"]) != 0:

                    # отсев файлов с необрабатывамыми расширениями
                    for doc_info in received_message["documents_info"]:
                        title = doc_info["title"]
                        link = doc_info["link"]
                        if not title or not link:
                            logger.warning('Invalid document info: %s', doc_info)
                            continue
                        for ext in EXTENSIONS:
                            if "." + ext in title:
                                result.append({"link": link, "title": title, "extension": ext})
                                break
                        received_message["documents_info"] = result

                    logger.info("Publish receive message by one %s" % received_message)

                    try:
                        await self.db_service.create(ContractDataModel(**received_message))
                    except IntegrityError:
                        logger.info("Запись уже существует")
                    except SQLAlchemyError as e:
                        logger.error("Ошибка при записи в базу данных: %s" % e)
                    except Exception as e:
                        logger.error("Общая ошибка консьюмера веб-парсинга: %s" % e)
                    else:
                        logger.info("Created in psql. Start publish...")
                        async with self.producer as prdr:
                            await prdr.publish(
                                message=json.dumps(
                                    {
                                        "site_url": received_message["site_url"],
                                        "tender_number": received_message["tender_number"],
                                        "documents_info": received_message["documents_info"][0]
                                    }
                                )
                            )
                        logger.info("Publish ended...")
                else:
                    logger.info("У тендера нет вложений.В базе контрактов ничего не создано и"
                                " в нейропарсинг ничего не отправлено")
