from functools import lru_cache
from typing import Set

import duckdb


@lru_cache()
def get_core_config() -> Set[str]:
    rows = (
        duckdb.connect(":memory:")
        .execute("SELECT name FROM duckdb_settings()")
        .fetchall()
    )
    return {name for name, in rows}
