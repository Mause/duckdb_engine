from pytest import fixture
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import registry


@fixture
def engine() -> Engine:
    registry.register("duckdb", "duckdb_engine", "Dialect")

    return create_engine("duckdb:///:memory:")
