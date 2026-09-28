"""Reflection must use the namespace of the requested attached database."""

import pytest
import sqlalchemy
from sqlalchemy import create_engine, inspect


@pytest.mark.skipif(sqlalchemy.__version__ < "2.0", reason="SQLAlchemy 2 reflection")
@pytest.mark.parametrize("catalog", ["other", "other db"])
def test_attached_relation_namespace(catalog: str) -> None:
    from sqlalchemy.engine.reflection import (  # type: ignore[attr-defined]
        ObjectKind,
        ObjectScope,
    )

    engine = create_engine("duckdb:///:memory:")
    quoted = '"' + catalog.replace('"', '""') + '"'
    schema = f"{quoted}.main"
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql(f"ATTACH ':memory:' AS {quoted}")
            connection.exec_driver_sql("CREATE TABLE main.t (wrong INTEGER)")
            connection.commit()  # type: ignore[attr-defined]
            connection.exec_driver_sql(
                f"CREATE TABLE {quoted}.main.t (correct VARCHAR)"
            )
            connection.exec_driver_sql(
                f"CREATE TABLE {quoted}.main.only_there (id INTEGER)"
            )
            connection.exec_driver_sql(
                f"COMMENT ON TABLE {quoted}.main.t IS 'attached'"
            )
            inspector = inspect(connection)
            assert inspector.get_table_comment("t", schema) == {"text": "attached"}
            assert inspector.get_table_comment("only_there", schema) == {"text": None}
            oids = engine.dialect._get_table_oids(  # type: ignore[attr-defined]
                connection, schema, ["t"], ObjectScope.DEFAULT, ObjectKind.TABLE
            )
            assert oids == [(inspector.get_table_oid("t", schema), "t")]  # type: ignore[attr-defined]
            assert inspector.get_table_comment("t") == {"text": None}
    finally:
        engine.dispose()
