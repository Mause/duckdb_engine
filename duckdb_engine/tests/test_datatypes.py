from typing import Type

from pytest import mark
from sqlalchemy import Column, Integer
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

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
