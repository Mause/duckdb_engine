from typing import Any, Dict, List, Tuple, Type

import duckdb
from sqlalchemy import types as sqltypes
from sqlalchemy import util
from sqlalchemy.dialects.postgresql import dialect as postgres_dialect
from sqlalchemy.dialects.postgresql.base import PGExecutionContext, PGInspector
from sqlalchemy.engine.url import URL

name = "duckdb"


class DBAPI:
    paramstyle = "qmark"

    class Error(Exception):
        pass


class DuckDBInspector(PGInspector):
    def get_check_constraints(
        self, table_name: str, schema: str = None, **kw: Any
    ) -> List[Dict[str, Any]]:
        try:
            return super().get_check_constraints(table_name, schema, **kw)
        except Exception as e:
            raise NotImplementedError() from e


class ConnectionWrapper:
    c: duckdb.DuckDBPyConnection
    notices: List[str]

    def __init__(self, c: duckdb.DuckDBPyConnection) -> None:
        self.c = c
        self.notices = list()

    def cursor(self) -> "ConnectionWrapper":
        return self

    def fetchmany(self, size: int = None) -> List:
        # TODO: remove this once duckdb supports fetchmany natively
        try:
            # TODO: add size parameter here once the next duckdb version is released
            return (self.c.fetch_df_chunk()).values.tolist()
        except RuntimeError as e:
            if e.args[0].startswith(
                "Invalid Input Error: Attempting to fetch from an unsuccessful or closed streaming query result"
            ):
                return []
            else:
                raise e

    def __getattr__(self, name: str) -> Any:
        return getattr(self.c, name)

    @property
    def connection(self) -> "ConnectionWrapper":
        return self

    def close(self) -> None:
        # duckdb doesn't support 'soft closes'
        pass

    @property
    def rowcount(self) -> int:
        return -1

    def executemany(
        self, statement: str, parameters: List[Dict] = None, context: Any = None
    ) -> None:
        self.c.executemany(statement, parameters)

    def execute(
        self, statement: str, parameters: Tuple = None, context: Any = None
    ) -> None:
        try:
            if statement.lower() == "commit":  # this is largely for ipython-sql
                self.c.commit()
            elif statement.lower() == "register":
                assert parameters and len(parameters) == 2, parameters
                view_name, df = parameters
                self.c.register(view_name, df)
            elif parameters is None:
                self.c.execute(statement)
            else:
                self.c.execute(statement, parameters)
        except RuntimeError as e:
            if e.args[0].startswith("Not implemented Error"):
                raise NotImplementedError(*e.args) from e
            elif (
                e.args[0]
                == "TransactionContext Error: cannot commit - no transaction is active"
            ):
                return
            else:
                raise e


class Dialect(postgres_dialect):
    _has_events = False
    identifier_preparer = None
    inspector = DuckDBInspector
    # colspecs TODO: remap types to duckdb types
    colspecs = util.update_copy(
        postgres_dialect.colspecs,
        {
            # the psycopg2 driver registers a _PGNumeric with custom logic for
            # postgres type_codes (such as 701 for float) that duckdb doesn't have
            sqltypes.Numeric: sqltypes.Numeric,
        },
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["use_native_hstore"] = False
        super().__init__(*args, **kwargs)

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
        self,
        cursor: ConnectionWrapper,
        statement: str,
        parameters: Any,
        context: PGExecutionContext,
    ) -> None:
        cursor.execute(statement, parameters, context)

    def do_executemany(
        self,
        cursor: ConnectionWrapper,
        statement: str,
        parameters: List[Any],
        context: PGExecutionContext = None,
    ) -> None:
        cursor.executemany(statement, parameters, context)

    @staticmethod
    def dbapi() -> Type[DBAPI]:
        return DBAPI

    def create_connect_args(self, u: URL) -> Tuple[Tuple, Dict]:
        return (), {"database": u.__to_string__(hide_password=False).split("///")[1]}

    def _get_server_version_info(
        self, connection: ConnectionWrapper
    ) -> Tuple[int, int]:
        return (8, 0)

    def get_default_isolation_level(self, connection: ConnectionWrapper) -> None:
        raise NotImplementedError()

    def do_rollback(self, connection: ConnectionWrapper) -> None:
        try:
            super().do_rollback(connection)
        except RuntimeError as e:
            if (
                e.args[0]
                != "TransactionContext Error: cannot rollback - no transaction is active"
            ):
                raise e

    def do_begin(self, connection: ConnectionWrapper) -> None:
        connection.execute("begin")

    @classmethod
    def get_dialect_cls(cls, u: str) -> Type["Dialect"]:
        return cls


dialect = Dialect
