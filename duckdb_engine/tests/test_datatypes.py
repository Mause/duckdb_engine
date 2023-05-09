from typing import Type
from uuid import uuid4

from pytest import importorskip, mark
from sqlalchemy import Column, Integer, MetaData, Table, inspect, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.types import JSON

from ..datatypes import types


@mark.parametrize("coltype", types)
def test_unsigned_integer_type(
    engine: Engine, session: Session, coltype: Type[Integer]
) -> None:
    Base = declarative_base()

    tname = "table"
    table = type(
        "Table",
        (Base,),
        {
            "__tablename__": tname,
            "id": Column(Integer, primary_key=True, default=0),
            "a": Column(coltype),
        },
    )
    Base.metadata.create_all(engine)

    has_table = (
        engine.has_table if hasattr(engine, "has_table") else inspect(engine).has_table
    )

    assert has_table(tname)

    session.add(table(a=1))
    session.commit()

    assert session.query(table).one()


def test_json(engine: Engine, session: Session) -> None:
    base = declarative_base()

    class Entry(base):
        __tablename__ = "test_json"

        id = Column(Integer, primary_key=True, default=0)
        meta = Column(JSON, nullable=False)

    base.metadata.create_all(bind=engine)

    session.add(Entry(meta={"hello": "world"}))  # type: ignore[call-arg]
    session.commit()

    result = session.query(Entry).one()

    assert result.meta == {"hello": "world"}


def test_uuid(engine: Engine, session: Session) -> None:
    importorskip("duckdb", "0.7.1")
    base = declarative_base()

    class Entry(base):
        __tablename__ = "test_uuid"

        id = Column(UUID, primary_key=True, default=0)

    base.metadata.create_all(bind=engine)

    ident = uuid4()

    session.add(Entry(id=ident))  # type: ignore[call-arg]
    session.commit()

    result = session.query(Entry).one()

    assert result.id == ident


def test_double_in_sqla_v2(engine: Engine) -> None:
    with engine.begin() as con:
        con.execute(text("CREATE TABLE t (x DOUBLE)"))
        con.execute(text("INSERT INTO t VALUES (1.0), (2.0), (3.0)"))

    md = MetaData()

    t = Table("t", md, autoload_with=engine)

    with engine.begin() as con:
        con.execute(t.select())
