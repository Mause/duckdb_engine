from pathlib import Path
from typing import cast

from snapshottest.module import SnapshotTest
from sqlalchemy import Column, Integer, String, alias, select, table
from sqlalchemy.engine import Engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import FromClause

from duckdb_engine.datatypes import Struct

Base = declarative_base()
path = Path(__file__).parent / "simple.parquet"


class Simple(Base):
    __tablename__ = str(path)
    itemType = Column(Integer, primary_key=True)
    stateId = Column(Struct)
    stateMeta = Column(Struct)
    style = Column(String)
    description = Column(String)


def test_reflection(engine: Engine, snapshot: SnapshotTest) -> None:
    users_table = table(str(path))
    users = select(users_table).add_columns("*")
    assert str(users.compile(bind=engine)).startswith("SELECT *")

    with engine.connect() as conn:
        res = conn.execute(users).fetchall()
        snapshot.assert_match(res)


def test_parquet_with_declarative_base(engine: Engine, snapshot: SnapshotTest) -> None:
    query = select(alias(cast(FromClause, Simple), "simple"))
    snapshot.assert_match(str(query.compile(bind=engine)))

    with engine.connect() as conn:
        res = conn.execute(query).fetchall()
        snapshot.assert_match(res)
