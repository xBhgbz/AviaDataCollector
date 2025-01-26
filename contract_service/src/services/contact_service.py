from typing import Protocol, Any

from loguru import logger
from sqlalchemy import update, and_, select, insert
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import psql_config
from db.postgres import get_session
from models.entity import ContractData
from schemas.entity import ContractDataModel, GetFieldContractData, ContractForAdminModel


class DBService(Protocol):
    """Интерфейс взаимодействия с базой"""

    async def create(self, data) -> bool:
        """Создает новую запись в таблице contract_data."""

    async def update(self, data, update_values: dict):
        """Обновление записи контракта"""

    async def get_field(self, data, *args):
        """Получение значения конкретного поля в записи."""

    async def get_contract_data(self, data):
        """Получение информации о контракте"""


class PsqlService:
    def __init__(self, config):
        self.config = config

    async def create(self, data: ContractDataModel) -> bool:
        """Создает новую запись в таблице contract_data."""

        logger.info("Создание записи ContractData с номером %s в базе данных..." % data.tender_number)

        async for db in get_session():
            contract_data = ContractData(**data.model_dump())
            db.add(contract_data)
            await db.flush()
            await db.commit()
            logger.info("Запись ContractData успешно создана")
            return True

    async def update(self, data: GetFieldContractData, update_values: dict):
        """Обновление записи контракта"""
        logger.info("Обновление записи ContractData с номером %s в базе данных..." % data.tender_number)

        async for db in get_session():
            await db.execute(
                update(ContractData).where(
                    and_(
                        ContractData.tender_number == data.tender_number,
                        ContractData.site_url == data.site_url
                    )
                ).values(**update_values)
            )
            await db.commit()

    async def get_field(self, data: GetFieldContractData, field_name: str) -> Any:
        """Получение значения конкретного поля в записи ContractData."""

        logger.info("Получение поля '%s' для контракта с номером %s" % (field_name, data.tender_number))
        logger.info("DATA: %s %s" % (data.tender_number, data.site_url))

        async for db in get_session():
            query = select(getattr(ContractData, field_name)).where(
                and_(
                    ContractData.tender_number == data.tender_number,
                    ContractData.site_url == data.site_url
                )
            )
            result = await db.execute(query)
            field_value = result.scalar_one_or_none()
            logger.info(f"Поле '{field_name}' для контракта {data.tender_number}: {field_value}")
            return field_value

    async def get_contract_data(self, data: GetFieldContractData) -> ContractForAdminModel:
        """Получение информации о контракте"""

        logger.info("Получение информации для контракта с номером %s" % data.tender_number)

        async for db in get_session():
            query = select(ContractData).where(
                and_(
                    ContractData.tender_number == data.tender_number,
                    ContractData.site_url == data.site_url
                )
            )
            result = await db.execute(query)
            field = result.scalar()
            return ContractForAdminModel(
                site_url=field.site_url,
                tender_info_link=field.tender_info_link,
                tender_number=field.tender_number,
                purchase_object=field.purchase_object,
                customer=field.customer,
                price=field.price
            )


psql_service = PsqlService(psql_config)





