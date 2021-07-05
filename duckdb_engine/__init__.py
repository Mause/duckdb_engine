from dataclasses import dataclass, field
from typing import Any, Dict, List, Tuple, Type

import duckdb
from sqlalchemy.dialects.postgresql import dialect as postgres_dialect
from sqlalchemy.engine import URL


class DBAPI:
    paramstyle = "qmark"

    class Error(Exception):
        pass


@dataclass
class ConnectionWrapper:
    c: duckdb.DuckDBPyConnection
    notices: List[str] = field(default_factory=list)

    def cursor(self) -> "ConnectionWrapper":
        return self

    def fetchmany(self, size: int = None) -> List:
        # TODO: remove this once duckdb supports fetchmany natively
        return self.c.fetch_df_chunk().values.tolist()

    def __getattr__(self, name: str) -> Any:
        return getattr(self.c, name)

    @property
    def connection(self) -> "ConnectionWrapper":
        return self

    def close(self) -> None:
        # duckdb doesn't support 'soft closes'
        pass

    def execute(
        self, statement: str, parameters: Dict = None, context: Any = None
    ) -> None:
        if parameters is None:
            self.c.execute(statement)
        else:
            self.c.execute(statement, parameters)


class Dialect(postgres_dialect):
    _has_events = False
    identifier_preparer = None
    # colspecs TODO: remap types to duckdb types

    def connect(self, *args: Any, **kwargs: Any) -> ConnectionWrapper:
        return ConnectionWrapper(duckdb.connect(*args, **kwargs))

    def on_connect(self) -> None:
        pass

    def ddl_compiler(
        self, dialect: str, ddl: Any, **kwargs: Any
    ) -> postgres_dialect.ddl_compiler:
        # TODO: enforce no `serial` type

        # duckdb doesn't support foreign key constraints (yet)
        ddl.include_foreign_key_constraints = {}
        return postgres_dialect.ddl_compiler(dialect, ddl, **kwargs)

    def do_execute(
        self, cursor: ConnectionWrapper, statement: str, parameters: Any, context: Any
    ) -> None:
        cursor.execute(statement, parameters, context)

    @staticmethod
    def dbapi() -> Type[DBAPI]:
        return DBAPI

    def create_connect_args(self, u: URL) -> Tuple[Tuple, Dict]:
        return (), {"database": u.render_as_string(hide_password=False).split("///")[1]}

    def initialize(self, connection: ConnectionWrapper) -> None:
        pass

    def do_rollback(self, connection: ConnectionWrapper) -> None:
        pass

    @classmethod
    def get_dialect_cls(cls, u: str) -> Type["Dialect"]:
        return cls


dialect = Dialect
