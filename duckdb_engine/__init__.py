import warnings
from typing import Any, Dict, List, Tuple, Type, cast

import duckdb
from sqlalchemy import Column, Sequence, pool
from sqlalchemy import types as sqltypes
from sqlalchemy import util
from sqlalchemy.dialects.postgresql import dialect as postgres_dialect
from sqlalchemy.dialects.postgresql.base import PGExecutionContext, PGInspector
from sqlalchemy.engine.url import URL
from sqlalchemy.sql.ddl import CreateTable

__version__ = "0.3.4"


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

    def __init__(self, c: duckdb.DuckDBPyConnection) -> None:
        self.c = c
        self.notices = list()

    def cursor(self) -> "ConnectionWrapper":
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


class DuckDBEngineWarning(Warning):
    pass


def remove_serial_columns(ddl: "CreateTable", generate_sequences: bool) -> None:
    for column in ddl.columns:
        el = cast(Column, column.element)
        if el.primary_key and generate_sequences:
            warnings.warn(
                "Generating a named sequence for your table - this is probably very buggy",
                category=DuckDBEngineWarning,
            )
            seq: Sequence = Sequence(ddl.element.name + "_" + el.name + "_seq")
            el.default = seq
            el.server_default = seq.next_value()


class Dialect(postgres_dialect):
    name = "duckdb"
    driver = "duckdb_engine"
    _has_events = False
    identifier_preparer = None
    supports_statement_cache = False
    supports_comments = False
    supports_sane_rowcount = False
    inspector = DuckDBInspector
    # colspecs TODO: remap types to duckdb types
    colspecs = util.update_copy(
        postgres_dialect.colspecs,
        {
            # the psycopg2 driver registers a _PGNumeric with custom logic for
            # postgres type_codes (such as 701 for float) that duckdb doesn't have
            sqltypes.Numeric: sqltypes.Numeric,
            sqltypes.Interval: sqltypes.Interval,
        },
    )

    def __init__(self, generate_sequences: bool = False, **kwargs: Any) -> None:
        self.generate_sequences = generate_sequences
        kwargs["use_native_hstore"] = False
        super().__init__(**kwargs)

    def connect(
        self, database: str, read_only: bool = False, config: Dict = None
    ) -> ConnectionWrapper:
        return ConnectionWrapper(duckdb.connect(database, read_only, config or {}))

    def on_connect(self) -> None:
        pass

    def ddl_compiler(
        self, dialect: str, ddl: Any, **kwargs: Any
    ) -> postgres_dialect.ddl_compiler:

        if isinstance(ddl, CreateTable):
            remove_serial_columns(ddl, self.generate_sequences)

        return postgres_dialect.ddl_compiler(dialect, ddl, **kwargs)

    def do_execute(
        self,
        cursor: ConnectionWrapper,
        statement: str,
        parameters: Any,
        context: PGExecutionContext,
    ) -> None:
        cursor.execute(statement, parameters, context)

    @classmethod
    def get_pool_class(cls, url: URL) -> Type[pool.Pool]:
        if url.database == ":memory:":
            return pool.SingletonThreadPool
        else:
            return pool.QueuePool

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
        if hasattr(u, "render_as_string"):
            # Compatible with SQLAlchemy >= 1.4
            string_representation = u.render_as_string(hide_password=False)  # type: ignore
        else:
            # Compatible with SQLAlchemy < 1.4
            string_representation = u.__to_string__(hide_password=False)
        return (), {"database": string_representation.split("///")[1]}

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

    def get_view_names(
        self, connection: ConnectionWrapper, schema: str = None, **kwargs: Any
    ) -> List[str]:
        s = "SELECT name FROM sqlite_master WHERE type='view' ORDER BY name"
        rs = connection.exec_driver_sql(s)

        return [row[0] for row in rs]
