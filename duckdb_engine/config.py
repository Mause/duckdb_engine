from functools import lru_cache
from typing import Dict, Set

import duckdb
from sqlalchemy import String
from sqlalchemy.engine import Dialect


@lru_cache()
def get_core_config() -> Set[str]:
    rows = (
        duckdb.connect(":memory:")
        .execute("SELECT name FROM duckdb_settings()")
        .fetchall()
    )
    return {name for name, in rows}


def apply_config(
    dialect: Dialect, conn: duckdb.DuckDBPyConnection, ext: Dict[str, str]
) -> None:
    process = String().literal_processor(dialect=dialect)
    for k, v in ext.items():
        conn.execute(f"SET {k} = {process(v)}")
