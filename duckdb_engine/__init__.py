from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type

import duckdb
from sqlalchemy import pool
from sqlalchemy import types as sqltypes
from sqlalchemy import util
from sqlalchemy.dialects.postgresql.base import PGInspector, PGTypeCompiler
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.compiler import compiles

from . import datatypes
from .config import apply_config, get_core_config

__version__ = "0.6.1"

if TYPE_CHECKING:
    from sqlalchemy.base import Connection


@compiles(datatypes.UInt64, "duckdb")  # type: ignore
@compiles(datatypes.UInt32, "duckdb")  # type: ignore
@compiles(datatypes.UInt16, "duckdb")  # type: ignore
@compiles(datatypes.UInt8, "duckdb")  # type: ignore
def compile_uint(element: sqltypes.Integer, compiler: PGTypeCompiler, **kw: Any) -> str:
    return type(element).__name__


class DBAPI:
    paramstyle = duckdb.paramstyle
    apilevel = duckdb.apilevel
    threadsafety = duckdb.threadsafety

    # this is being fixed upstream to add a proper exception hierarchy
    Error = getattr(duckdb, "Error", RuntimeError)

    @staticmethod
    def Binary(x: Any) -> Any:
        return x


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
    autocommit = None  # duckdb doesn't support setting autocommit
    closed = False

    def __init__(self, c: duckdb.DuckDBPyConnection) -> None:
        self.c = c
        self.notices = list()

    def cursor(self) -> "Connection":
        return self

    def fetchmany(self, size: int = None) -> List:
        # TODO: remove this once duckdb supports fetchmany natively
        try:
            # TODO: add size parameter here once the next duckdb version is released
            return (self.c.fetch_df_chunk()).values.tolist()  # type: ignore
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
    def connection(self) -> "Connection":
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


class DuckDBEngineWarning(Warning):
    pass


class Dialect(PGDialect_psycopg2):
    name = "duckdb"
    driver = "duckdb_engine"
    _has_events = False
    supports_statement_cache = False
    supports_comments = False
    supports_sane_rowcount = False
    inspector = DuckDBInspector
    # colspecs TODO: remap types to duckdb types
    colspecs = util.update_copy(
        PGDialect_psycopg2.colspecs,
        {
            # the psycopg2 driver registers a _PGNumeric with custom logic for
            # postgres type_codes (such as 701 for float) that duckdb doesn't have
            sqltypes.Numeric: sqltypes.Numeric,
            sqltypes.Interval: sqltypes.Interval,
        },
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs["use_native_hstore"] = False
        super().__init__(*args, **kwargs)

    def connect(self, *cargs: Any, **cparams: Any) -> "Connection":

        core_keys = get_core_config()
        preload_extensions = cparams.pop("preload_extensions", [])
        config = cparams.get("config", {})

        ext = {k: config.pop(k) for k in list(config) if k not in core_keys}

        conn = duckdb.connect(*cargs, **cparams)

        for extension in preload_extensions:
            conn.execute(f"LOAD {extension}")

        apply_config(self, conn, ext)

        return ConnectionWrapper(conn)

    def on_connect(self) -> None:
        pass

    @classmethod
    def get_pool_class(cls, url: URL) -> Type[pool.Pool]:
        if url.database == ":memory:":
            return pool.SingletonThreadPool
        else:
            return pool.QueuePool

    @staticmethod
    def dbapi() -> Type[DBAPI]:
        return DBAPI

    def _get_server_version_info(self, connection: "Connection") -> Tuple[int, int]:
        return (8, 0)

    def get_default_isolation_level(self, connection: "Connection") -> None:
        raise NotImplementedError()

    def do_rollback(self, connection: "Connection") -> None:
        try:
            super().do_rollback(connection)
        except RuntimeError as e:
            if (
                e.args[0]
                != "TransactionContext Error: cannot rollback - no transaction is active"
            ):
                raise e

    def do_begin(self, connection: "Connection") -> None:
        connection.execute("begin")

    def get_view_names(
        self,
        connection: Any,
        schema: Optional[Any] = ...,
        include: Any = ...,
        **kw: Any,
    ) -> Any:
        s = "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name"
        rs = connection.exec_driver_sql(s)

        return [row[0] for row in rs]
