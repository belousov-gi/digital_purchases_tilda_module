from app.core.config import settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase

connect_args={"timeout": 300}

async_engine = create_async_engine(settings.ASYNC_DATABASE_URL,connect_args=connect_args)
async_session_maker = async_sessionmaker(async_engine, class_=AsyncSession)

class Base(DeclarativeBase):
    pass

async def get_async_session():
    async with async_session_maker() as session:
        yield session
