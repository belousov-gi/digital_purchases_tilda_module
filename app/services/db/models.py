from typing import Optional

from app.services.db.database import Base
from sqlalchemy import BigInteger
from sqlalchemy.orm import Mapped, mapped_column


class Consumer(Base):
    __tablename__ = "consumer"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, index=True, autoincrement=True)
    email: Mapped[str] = mapped_column(nullable=False)

class Product(Base):
    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, autoincrement=True)
    name: Mapped[str]
    description: Mapped[Optional[str]]
    price: Mapped[int]
    file_format: Mapped[str]


class Purchase(Base):
    __tablename__ = "purchase"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_consumer: Mapped[int] = mapped_column(BigInteger, index=True)
    id_product: Mapped[int]
    id_tilda_order: Mapped[str]
    timestamp: Mapped[int] = mapped_column(BigInteger)
    file_format: Mapped[str]
    purchase_name: Mapped[str]
    URL: Mapped[str]
    consumer_email: Mapped[str]

class Code(Base):
    __tablename__ = "code"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_consumer: Mapped[int] = mapped_column(BigInteger, index=True)
    value: Mapped[int]
    created_at: Mapped[int] = mapped_column(BigInteger)
    entering_attempts:  Mapped[int]
    is_succeeded: Mapped[bool]


class M2MToken(Base):
    __tablename__ = "m2mtoken"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    service_name: Mapped[str] = mapped_column(nullable=False)
    m2m_token: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[str] = mapped_column(nullable=False)
