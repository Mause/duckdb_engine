import warnings
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Type, cast

import duckdb
from sqlalchemy import pool, text
from sqlalchemy import types as sqltypes
from sqlalchemy import util
from sqlalchemy.dialects.postgresql.base import PGInspector
from sqlalchemy.dialects.postgresql.psycopg2 import PGDialect_psycopg2
from sqlalchemy.engine.url import URL

from .config import apply_config, get_core_config
from .datatypes import register_extension_types

__version__ = "0.6.8"

if TYPE_CHECKING:
    from sqlalchemy.base import Connection
    from sqlalchemy.engine.interfaces import _IndexDict


register_extension_types()


class DBAPI:
    paramstyle = duckdb.paramstyle
    apilevel = duckdb.apilevel
    threadsafety = duckdb.threadsafety

    # this is being fixed upstream to add a proper exception hierarchy
    Error = getattr(duckdb, "Error", RuntimeError)
    TransactionException = getattr(duckdb, "TransactionException", Error)
    ParserException = getattr(duckdb, "ParserException", Error)

    @staticmethod
    def Binary(x: Any) -> Any:
        return x


class DuckDBInspector(PGInspector):
    def get_check_constraints(
        self, table_name: str, schema: Optional[str] = None, **kw: Any
    ) -> List[Dict[str, Any]]:
        try:
            return super().get_check_constraints(table_name, schema, **kw)
        except Exception as e:
            raise NotImplementedError() from e


class ConnectionWrapper:
    __c: duckdb.DuckDBPyConnection
    notices: List[str]
    autocommit = None  # duckdb doesn't support setting autocommit
    closed = False

    def __init__(self, c: duckdb.DuckDBPyConnection) -> None:
        self.__c = c
        self.notices = list()

    def cursor(self) -> "Connection":
        return self

    def fetchmany(self, size: Optional[int] = None) -> List:
        if hasattr(self.__c, "fetchmany"):
            # fetchmany was only added in 0.5.0
            if size is None:
                return self.__c.fetchmany()
            else:
                return self.__c.fetchmany(size)

        try:
            return cast(list, self.__c.fetch_df_chunk().values.tolist())
        except RuntimeError as e:
            if e.args[0].startswith(
                "Invalid Input Error: Attempting to fetch from an unsuccessful or closed streaming query result"
            ):
                return []
            else:
                raise e

    @property
    def c(self) -> duckdb.DuckDBPyConnection:
        warnings.warn(
            "Directly accessing the internal connection object is deprecated (please go via the __getattr__ impl)",
            DeprecationWarning,
        )
        return self.__c

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__c, name)

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
        self,
        statement: str,
        parameters: Optional[List[Dict]] = None,
        context: Optional[Any] = None,
    ) -> None:
        self.__c.executemany(statement, parameters)

    def execute(
        self,
        statement: str,
        parameters: Optional[Tuple] = None,
        context: Optional[Any] = None,
    ) -> None:
        try:
            if statement.lower() == "commit":  # this is largely for ipython-sql
                self.__c.commit()
            elif statement.lower() == "register":
                assert parameters and len(parameters) == 2, parameters
                view_name, df = parameters
                self.__c.register(view_name, df)
            elif parameters is None:
                self.__c.execute(statement)
            else:
                self.__c.execute(statement, parameters)
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
    supports_server_side_cursors = False
    inspector = DuckDBInspector
    # colspecs TODO: remap types to duckdb types
    colspecs = util.update_copy(
        PGDialect_psycopg2.colspecs,
        {
            # the psycopg2 driver registers a _PGNumeric with custom logic for
            # postgres type_codes (such as 701 for float) that duckdb doesn't have
            sqltypes.Numeric: sqltypes.Numeric,
            sqltypes.Interval: sqltypes.Interval,
            sqltypes.JSON: sqltypes.JSON,
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
    def dbapi(**kwargs: Any) -> Type[DBAPI]:
        return DBAPI

    def _get_server_version_info(self, connection: "Connection") -> Tuple[int, int]:
        return (8, 0)

    def get_default_isolation_level(self, connection: "Connection") -> None:
        raise NotImplementedError()

    def do_rollback(self, connection: "Connection") -> None:
        try:
            super().do_rollback(connection)
        except DBAPI.TransactionException as e:
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
        schema: Optional[Any] = None,
        include: Optional[Any] = None,
        **kw: Any,
    ) -> Any:
        s = "SELECT table_name FROM information_schema.tables WHERE table_type='VIEW' and table_schema=:schema_name"
        rs = connection.execute(
            text(s), {"schema_name": schema if schema is not None else "main"}
        )

        return [row[0] for row in rs]

    def get_indexes(
        self,
        connection: "Connection",
        table_name: str,
        schema: Optional[str] = None,
        **kw: Any,
    ) -> List["_IndexDict"]:
        warnings.warn(
            "duckdb-engine doesn't yet support reflection on indices",
            DuckDBEngineWarning,
        )
        return []
