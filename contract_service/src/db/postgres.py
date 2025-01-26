from loguru import logger
from sqlalchemy.orm import DeclarativeBase, sessionmaker
import sqlalchemy as sa
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

from core.config import psql_config


class Base(DeclarativeBase):
    metadata = sa.MetaData()


dsn = f"postgresql+asyncpg://{psql_config.CONTRACT_POSTGRES_USER}:" \
      f"{psql_config.CONTRACT_POSTGRES_PASSWORD}@{psql_config.CONTRACT_POSTGRES_HOST}:" \
      f"{psql_config.CONTRACT_POSTGRES_PORT}/{psql_config.CONTACT_DB}"

dsn_for_alembic = f"postgresql+psycopg2://{psql_config.CONTRACT_POSTGRES_USER}:" \
      f"{psql_config.CONTRACT_POSTGRES_PASSWORD}@{psql_config.CONTRACT_POSTGRES_HOST}:" \
      f"{psql_config.CONTRACT_POSTGRES_PORT}/{psql_config.CONTACT_DB}"

engine = create_async_engine(dsn, echo=True, future=True)

async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session():
    """Получение сессии"""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("Error in get_session: %s" % e)
            raise e
