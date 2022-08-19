from typing import Type

from pytest import mark
from sqlalchemy import Column, Integer, MetaData, Table, inspect
from sqlalchemy.engine import Engine

from .. import datatypes as dt


@mark.parametrize("coltype", [dt.UInt8, dt.UInt16, dt.UInt32, dt.UInt64])
def test_unsigned_integer_type(engine: Engine, coltype: Type[Integer]) -> None:
    tname = "table"
    meta = MetaData(engine)
    Table(
        tname,
        meta,
        Column(
            "a",
            coltype,
        ),
    )
    meta.create_all()
    assert inspect(engine).has_table(tname)
