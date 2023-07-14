import warnings
from typing import Type
from uuid import uuid4

import duckdb
from pytest import importorskip, mark
from sqlalchemy import Column, Integer, MetaData, String, Table, inspect, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.sql import sqltypes
from sqlalchemy.types import JSON

from ..datatypes import Map, Struct, types


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


def test_all_types_reflection(engine: Engine) -> None:
    importorskip("sqlalchemy", "1.4.0")
    importorskip("duckdb", "0.5.1")

    with warnings.catch_warnings() as capture, engine.connect() as conn:
        conn.execute(text("create table t2 as select * from test_all_types()"))
        table = Table("t2", MetaData(), autoload_with=conn)
        for col in table.columns:
            name = col.name
            if name.endswith("_enum") and duckdb.__version__ < "0.7.1":  # type: ignore[attr-defined]
                continue
            if "array" in name or "struct" in name or "map" in name or "union" in name:
                assert col.type == sqltypes.NULLTYPE, name
            else:
                assert col.type != sqltypes.NULLTYPE, name
        assert not capture


def test_nested_types(engine: Engine, session: Session) -> None:
    importorskip("duckdb", "0.5.0")  # nested types require at least duckdb 0.5.0
    base = declarative_base()

    class Entry(base):
        __tablename__ = "test_struct"

        id = Column(Integer, primary_key=True, default=0)
        struct = Column(Struct(fields={"name": String}))
        map = Column(Map(String, Integer))
        # union = Column(Union(fields={"name": String, "age": Integer}))

    base.metadata.create_all(bind=engine)

    struct_data = {"name": "Edgar"}
    map_data = {"one": 1, "two": 2}

    session.add(Entry(struct=struct_data, map=map_data))  # type: ignore[call-arg]
    session.commit()

    result = session.query(Entry).one()

    assert result.struct == struct_data
    assert result.map == map_data
