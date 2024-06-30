from datetime import datetime

from pytest import mark
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Sequence,
    String,
    func,
    select,
)
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import Mapped, declarative_base, relationship, sessionmaker

Base = declarative_base()


class A(Base):
    __tablename__ = "a"

    id: int = Column(Integer, Sequence("id_seq"), primary_key=True)
    data: str = Column(String)
    create_date: datetime = Column(DateTime, server_default=func.now())
    bs: Mapped["B"] = relationship("B")

    # required in order to access columns with server defaults
    # or SQL expression defaults, after a flush, without
    # triggering an expired load
    __mapper_args__ = {"eager_defaults": True}


class B(Base):
    __tablename__ = "b"
    id: int = Column(Integer, Sequence("b_seq"), primary_key=True)
    a_id: int = Column(ForeignKey("a.id"))
    data = Column(String)


@mark.asyncio
async def test_asyncio() -> None:
    engine = create_async_engine("duckdb:///:memory:")
    async_session = sessionmaker(engine, class_=AsyncSession)
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as sess:
        async with sess.begin():
            sess.add(A(data="a1"))

        res = (await sess.execute(select(A))).scalars().one()
        assert res.data == "a1"

    await engine.dispose()
