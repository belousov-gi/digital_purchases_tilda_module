import app.services.db.models as db_models
from abc import ABC, abstractmethod
from app.exceptions.http_exc import VerificationCodeDoesntExist
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.functions import func
from app.core import logger_config
import logging

sqlalchemy_logger = logging.getLogger('sqlalchemy.engine')
logger = logging.getLogger(__name__)

class IDb(ABC):
    @abstractmethod
    async def get_last_consumer_code(self, id_consumer: int) -> db_models.Code | None:
        pass

    @abstractmethod
    async def mark_code_as_succeded(self, code: db_models.Code) -> None:
        pass

    @abstractmethod
    async def add_code_entering_attempt(self, id_consumer: int) -> None:
        pass

    @abstractmethod
    async def get_last_consumer_purchase(self, id_consumer: int) -> db_models.Purchase:
        pass

    @abstractmethod
    async def get_consumer(self, email: str) -> db_models.Consumer | None:
        pass

    @abstractmethod
    async def get_product(self, product_id: int) -> db_models.Product | None:
        pass

    @abstractmethod
    async def save_purchases(self, purchases: list[db_models.Purchase]) -> list[db_models.Purchase]:
        pass

    @abstractmethod
    async def save_consumer(self, email: str) -> db_models.Consumer:
        pass

    @abstractmethod
    async def save_new_verification_code(self, code: db_models.Code) -> db_models.Code:
        pass

    @abstractmethod
    async def get_m2m_token(self, service_name: str) -> str:
        pass

    @abstractmethod
    async def save_m2m_token(self, m2m_token_info: db_models.M2MToken):
        pass

    @abstractmethod
    async def count_requested_codes_from_timestamp(self, start_timestamp: int, id_consumer: int):
        pass


class PostgreRepo(IDb):

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_consumer(self, email: str) -> db_models.Consumer | None:
        logger.info("Input data: Email - %s", email)
        stmt = select(db_models.Consumer).where(db_models.Consumer.email == email)
        result = await self.session.execute(stmt)
        consumer = result.scalar_one_or_none()
        logger.info("Output data: consumer - %s", consumer.__dict__ if consumer else 'None')
        return consumer

    async def save_consumer(self, email: str) -> db_models.Consumer:
        logger.info("Input data: Email - %s", email)
        consumer = db_models.Consumer(email=email)
        self.session.add(consumer)
        await self.session.commit()
        await self.session.refresh(consumer)
        logger.info("Output data: consumer - %s", consumer.__dict__ if consumer else 'None')
        return consumer

    async def save_purchases(self, purchases: list[db_models.Purchase]) -> list[db_models.Purchase]:
        logger.info("Input data: purchases list - %s", [purchase.__dict__ for purchase in purchases])
        self.session.add_all(purchases)
        await self.session.commit()
        for purchase in purchases:
            await self.session.refresh(purchase)
        logger.info("Output data: purchases - %s", [purchase.__dict__ for purchase in purchases] if purchases else 'None')
        return purchases

    async def get_last_consumer_code(self, id_consumer: int) -> db_models.Code | None:
        logger.info("Input data: id_consumer : %s", id_consumer)
        stmt = (select(db_models.Code)
                .where(db_models.Code.id_consumer == id_consumer)
                .order_by(db_models.Code.created_at.desc()))
        result = await self.session.execute(stmt)
        code = result.first()
        if code:
            code = code[0]
        logger.info("Output data: code - %s",code.__dict__ if code else 'None')
        return code

    async def get_last_consumer_purchase(self, id_consumer: int) -> db_models.Purchase | None:
        logger.info("Input data: id_consumer - %s", id_consumer)
        stmt = (select(db_models.Purchase)
                .where(db_models.Purchase.id_consumer == id_consumer)
                .order_by(db_models.Purchase.timestamp.desc()))
        result = await self.session.execute(stmt)
        purchase = result.first()[0]
        logger.info("Output data: purchase - %s", purchase.__dict__ if purchase else 'None')
        return purchase

    async def get_product(self, product_id: int) -> db_models.Product | None:
        logger.info("Input data: product_id - %s", product_id)
        stmt = select(db_models.Product).where(db_models.Product.id == product_id)
        result = await self.session.execute(stmt)
        product = result.scalar_one_or_none()
        logger.info("Output data: product - %s", product.__dict__ if product else 'None')
        return product

    async def save_new_verification_code(self, code: db_models.Code) -> db_models.Code:
        logger.info("Input data: code - %s", code.__dict__)
        self.session.add(code)
        await self.session.commit()
        await self.session.refresh(code)
        logger.info("Output data: code - %s", code.__dict__ if code else 'None')
        return code

    async def get_m2m_token(self, service_name: str) -> str:
        logger.info("Input data: service_name - %s", service_name)
        stmt = select(db_models.M2MToken).where(db_models.M2MToken.service_name == service_name)
        result = await self.session.execute(stmt)
        token = result.scalar_one_or_none()
        return token

    async def save_m2m_token(self, m2m_token_info: db_models.M2MToken):
        logger.info("Input data: m2m_token_info - %s", m2m_token_info.__dict__)
        self.session.add(m2m_token_info)
        await self.session.commit()
        await self.session.refresh(m2m_token_info)
        return m2m_token_info

    async def mark_code_as_succeded(self, code: db_models.Code) -> None:
        logger.info("Input data: code - %s", code.__dict__)

        table = db_models.Code
        stmt = (update(table).where(and_(table.id_consumer == code.id_consumer, table.value == code.value))
                .values(is_succeeded=True))
        result = await self.session.execute(stmt)


        logger.info("Updated rows - %s", result.rowcount if result else 'None')

        if result.rowcount > 0:
            await self.session.commit()
        else:
            raise VerificationCodeDoesntExist(f'Input code info: {jsonable_encoder(code)}')

    async def add_code_entering_attempt(self, id_consumer: int) -> None:
        logger.info("Input data: id_consumer - %s", id_consumer)
        last_code = await self.get_last_consumer_code(id_consumer=id_consumer)
        logger.info("Last code - %s", last_code.__dict__ if last_code else 'None')

        if last_code:
            last_code.entering_attempts += 1
        else:
            raise VerificationCodeDoesntExist(f'Tried to find a code for id_consumer: {id_consumer}')

        await self.session.commit()

    async def count_requested_codes_from_timestamp(self, start_timestamp: int, id_consumer: int) -> int:
        logger.info("Input data: start_timestamp - %s, id_consumer - %s ", start_timestamp, id_consumer)

        table = db_models.Code
        stmt = select(func.count()).where(and_(table.created_at >= start_timestamp, table.id_consumer == id_consumer))
        result = await self.session.execute(stmt)
        quantity = result.scalar()

        logger.info("Output data: quantity of requested codes - %s", quantity if quantity else 'None')
        return quantity
