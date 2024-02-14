from functools import lru_cache
from typing import Dict, List, Optional, Set, Type, Union

import duckdb
from sqlalchemy import Boolean, Integer, String
from sqlalchemy.engine import Dialect
from sqlalchemy.sql.type_api import TypeEngine
from typing_extensions import TypedDict

from ._supports import has_extension_registry_support, has_extension_version_support

TYPES: Dict[Type, TypeEngine] = {int: Integer(), str: String(), bool: Boolean()}


@lru_cache()
def get_core_config() -> Set[str]:
    rows = (
        duckdb.connect(":memory:")
        .execute("SELECT name FROM duckdb_settings()")
        .fetchall()
    )
    # special case for motherduck here - they accept this config at extension load time
    return {name for name, in rows} | {"motherduck_token"}


def apply_config(
    dialect: Dialect,
    conn: duckdb.DuckDBPyConnection,
    ext: Dict[str, Union[str, int, bool]],
) -> None:
    # TODO: does sqlalchemy have something that could do this for us?
    processors = {k: v.literal_processor(dialect=dialect) for k, v in TYPES.items()}

    for k, v in ext.items():
        process = processors[type(v)]
        assert process, f"Not able to configure {k} with {v}"
        conn.execute(f"SET {k} = {process(v)}")


class ExtensionConfig(TypedDict):
    name: str
    registry: Optional[str]
    version: Optional[str]


ExtensionConfigOrName = Union[ExtensionConfig, str]


def _install_extensions(
    dialect: Dialect, preinstall_extensions: List[ExtensionConfigOrName]
) -> None:
    def build(ext: ExtensionConfigOrName) -> str:
        parts = []
        if isinstance(ext, str):
            name = ext
        else:
            name = ext["name"]
            if has_extension_registry_support:
                parts.append(f'FROM {process(ext["registry"])}')
            if has_extension_version_support:
                parts.append(f'VERSION {process(ext["version"])}')
        parts.insert(0, f"INSTALL {process(name)}")
        return " ".join(parts)

    process = String().literal_processor(dialect)
    with duckdb.connect() as conn:
        for ext in preinstall_extensions:
            conn.execute(build(ext))
