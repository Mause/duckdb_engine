from typing import Type

from pytest import mark
from sqlalchemy import Column, Integer
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
    assert engine.has_table(tname)

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
