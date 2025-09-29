import re
import warnings
from functools import lru_cache
from typing import (
    TYPE_CHECKING,
    Any,
    Collection,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
)

import duckdb
import sqlalchemy
from sqlalchemy import pool, select, sql, text, util
from sqlalchemy import types as sqltypes
from sqlalchemy.engine.default import DefaultDialect
from sqlalchemy.engine.interfaces import Dialect as RootDialect
from sqlalchemy.engine.reflection import cache, Inspector
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import bindparam, compiler
from sqlalchemy.sql.selectable import Select
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql.compiler import IdentifierPreparer

from ._supports import has_comment_support
from .config import apply_config, get_core_config
from .datatypes import ISCHEMA_NAMES, register_extension_types

__version__ = "0.17.0"
sqlalchemy_version = sqlalchemy.__version__
duckdb_version: str = duckdb.__version__
supports_attach: bool = duckdb_version >= "0.7.0"
supports_user_agent: bool = duckdb_version >= "0.9.2"

if TYPE_CHECKING:
    from sqlalchemy.base import Connection
    from sqlalchemy.engine.interfaces import _IndexDict
    from sqlalchemy.sql.type_api import _ResultProcessor

register_extension_types()


__all__ = [
    "Dialect",
    "ConnectionWrapper",
    "CursorWrapper",
    "DuckDBEngineWarning",
    "DuckDBInsert",
    "insert",
]




class DuckDBInspector(Inspector):
    """DuckDB-specific inspector using native duckdb_* functions"""

    def get_schema_names(self, **kw: Any) -> List[str]:
        """Return list of schema names using duckdb_schemas()"""
        if not supports_attach:
            # Fallback for older DuckDB versions
            return ["main"]

        query = """
            SELECT database_name, schema_name
            FROM duckdb_schemas()
            WHERE schema_name NOT LIKE 'pg\\_%' ESCAPE '\\'
            ORDER BY database_name, schema_name
        """
        rs = self.bind.execute(text(query))

        qs = self.dialect.identifier_preparer.quote_schema
        return [qs(".".join(row)) for row in rs]

    def get_table_names(self, schema: Optional[str] = None, **kw: Any) -> List[str]:
        """Return list of table names using duckdb_tables()"""
        if not supports_attach:
            # Fallback for older DuckDB versions
            query = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_type = 'BASE TABLE'
            """
            if schema:
                query += " AND table_schema = :schema"
                rs = self.bind.execute(text(query), {"schema": schema})
            else:
                rs = self.bind.execute(text(query))
            return [table for (table,) in rs]

        query = """
            SELECT table_name
            FROM duckdb_tables()
            WHERE schema_name NOT LIKE 'pg\\_%' ESCAPE '\\'
        """
        params = {}

        if schema:
            database_name, schema_name = self.dialect.identifier_preparer._separate(schema)
            if schema_name:
                query += " AND schema_name = :schema_name"
                params["schema_name"] = schema_name
            if database_name:
                query += " AND database_name = :database_name"
                params["database_name"] = database_name

        rs = self.bind.execute(text(query), params)
        return [table for (table,) in rs]

    def get_view_names(self, schema: Optional[str] = None, **kw: Any) -> List[str]:
        """Return list of view names using duckdb_views()"""
        if not supports_attach:
            # Fallback for older DuckDB versions
            query = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_type = 'VIEW'
            """
            if schema:
                query += " AND table_schema = :schema"
                rs = self.bind.execute(text(query), {"schema": schema})
            else:
                rs = self.bind.execute(text(query))
            return [view for (view,) in rs]

        query = """
            SELECT view_name
            FROM duckdb_views()
            WHERE schema_name NOT LIKE 'pg\\_%' ESCAPE '\\'
        """
        params = {}

        if schema:
            database_name, schema_name = self.dialect.identifier_preparer._separate(schema)
            if schema_name:
                query += " AND schema_name = :schema_name"
                params["schema_name"] = schema_name
            if database_name:
                query += " AND database_name = :database_name"
                params["database_name"] = database_name

        rs = self.bind.execute(text(query), params)
        return [view for (view,) in rs]


class ConnectionWrapper:
    """Wrapper for DuckDB connection to provide SQLAlchemy interface"""
    __c: duckdb.DuckDBPyConnection
    notices: List[str]
    autocommit = None  # DuckDB doesn't support setting autocommit
    closed = False

    def __init__(self, c: duckdb.DuckDBPyConnection) -> None:
        self.__c = c
        self.notices = list()

    def cursor(self) -> "CursorWrapper":
        return CursorWrapper(self.__c, self)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__c, name)

    def close(self) -> None:
        self.__c.close()
        self.closed = True


class CursorWrapper:
    """Wrapper for DuckDB cursor to provide SQLAlchemy interface"""
    __c: duckdb.DuckDBPyConnection
    __connection_wrapper: "ConnectionWrapper"

    def __init__(
        self, c: duckdb.DuckDBPyConnection, connection_wrapper: "ConnectionWrapper"
    ) -> None:
        self.__c = c
        self.__connection_wrapper = connection_wrapper

    def executemany(
        self,
        statement: str,
        parameters: Optional[List[Dict]] = None,
        context: Optional[Any] = None,
    ) -> None:
        self.__c.executemany(statement, list(parameters) if parameters else [])

    def execute(
        self,
        statement: str,
        parameters: Optional[Tuple] = None,
        context: Optional[Any] = None,
    ) -> None:
        try:
            if statement.lower() == "commit":  # for ipython-sql compatibility
                self.__c.commit()
            elif statement.lower() in (
                "register",
                "register(?, ?)",
                "register($1, $2)",
            ):
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

    @property
    def connection(self) -> "Connection":
        return self.__connection_wrapper

    def close(self) -> None:
        pass  # DuckDB doesn't support cursor closing

    @property
    def description(self):
        """Override description to normalize DuckDBPyType objects to hashable strings"""
        if not hasattr(self.__c, 'description') or self.__c.description is None:
            return None
        
        # Normalize DuckDBPyType to string for hashability
        normalized = []
        for col in self.__c.description:
            name, typ = col[0], col[1]
            # Convert unhashable DuckDBPyType to string
            try:
                hash(typ)
                normalized.append(col)
            except TypeError:
                # Replace unhashable type with string representation
                normalized.append((name, str(typ)) + col[2:])
        return tuple(normalized)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.__c, name)

    def fetchmany(self, size: Optional[int] = None) -> List:
        if size is None:
            return self.__c.fetchmany()
        else:
            return self.__c.fetchmany(size)


class DuckDBEngineWarning(Warning):
    """Warning raised by DuckDB engine"""
    pass


def index_warning() -> None:
    """Warn about missing index reflection support"""
    warnings.warn(
        "duckdb-engine doesn't yet support reflection on indices",
        DuckDBEngineWarning,
    )


class DuckDBIdentifierPreparer(IdentifierPreparer):
    """DuckDB identifier preparer with database.schema support"""

    def __init__(self, dialect: "Dialect", **kwargs: Any) -> None:
        super().__init__(dialect, **kwargs)

        # Add DuckDB reserved words
        self.reserved_words.update(
            {
                keyword_name
                for (keyword_name,) in duckdb.cursor()
                .execute(
                    "select keyword_name from duckdb_keywords() where keyword_category == 'reserved'"
                )
                .fetchall()
            }
        )

    def _separate(self, name: Optional[str]) -> Tuple[Optional[Any], Optional[str]]:
        """
        Separate database name and schema name from qualified name.
        Format: <db_name>.<schema_name>
        Names are quoted if they contain spaces or special characters.
        """
        database_name, schema_name = None, name
        if name is not None and "." in name:
            database_name, schema_name = (
                max(s) for s in re.findall(r'"([^.]+)"|([^.]+)', name)
            )
        return database_name, schema_name

    def format_schema(self, name: str) -> str:
        """Prepare a quoted schema name."""
        database_name, schema_name = self._separate(name)
        if database_name is None:
            return self.quote(name)
        return ".".join(self.quote(_n) for _n in [database_name, schema_name])

    def quote_schema(self, schema: str, force: Any = None) -> str:
        """
        Conditionally quote a schema name.

        :param schema: string schema name
        :param force: unused
        """
        return self.format_schema(schema)


class DuckDBTypeCompiler(compiler.GenericTypeCompiler):
    """DuckDB type compiler"""

    def visit_INTEGER(self, type_: sqltypes.INTEGER, **kw: Any) -> str:
        # DuckDB auto-increments INTEGER PRIMARY KEY
        return "INTEGER"

    def visit_BIGINT(self, type_: sqltypes.BIGINT, **kw: Any) -> str:
        # DuckDB auto-increments BIGINT PRIMARY KEY
        return "BIGINT"

    def visit_BOOLEAN(self, type_: sqltypes.BOOLEAN, **kw: Any) -> str:
        return "BOOLEAN"

    def visit_TEXT(self, type_: sqltypes.TEXT, **kw: Any) -> str:
        return "TEXT"

    def visit_FLOAT(self, type_: sqltypes.FLOAT, **kw: Any) -> str:
        return "DOUBLE"

    def visit_NUMERIC(self, type_: sqltypes.NUMERIC, **kw: Any) -> str:
        if type_.precision is not None and type_.scale is not None:
            return f"DECIMAL({type_.precision}, {type_.scale})"
        elif type_.precision is not None:
            return f"DECIMAL({type_.precision})"
        return "DECIMAL"

    def visit_JSON(self, type_: sqltypes.JSON, **kw: Any) -> str:
        return "JSON"


class DuckDBCompiler(compiler.SQLCompiler):
    """DuckDB SQL compiler"""
    pass


class DuckDBDDLCompiler(compiler.DDLCompiler):
    """DuckDB DDL compiler"""

    def get_column_specification(self, column, **kwargs):
        """Override to handle DuckDB-specific column specs"""
        spec = super().get_column_specification(column, **kwargs)
        return spec


class DuckDBNullType(sqltypes.NullType):
    """DuckDB-specific null type"""
    cache_ok = True

    def result_processor(
        self, dialect: RootDialect, coltype: sqltypes.TypeEngine
    ) -> Optional["_ResultProcessor"]:
        if coltype == "JSON":
            return sqltypes.JSON().result_processor(dialect, coltype)
        else:
            return super().result_processor(dialect, coltype)


class DuckDBInsert(Insert):
    """DuckDB INSERT statement with ON CONFLICT support"""
    inherit_cache = True

    def on_conflict_do_nothing(self, constraint=None):
        """Add ON CONFLICT DO NOTHING clause"""
        self._post_values_clause = sql.ClauseElement._construct_raw_text(
            "ON CONFLICT DO NOTHING"
        )
        return self

    def on_conflict_do_update(
        self,
        constraint=None,
        index_elements=None,
        index_where=None,
        set_=None,
        where=None,
    ):
        """Add ON CONFLICT DO UPDATE clause"""
        if set_ is None:
            raise ValueError("set_ dictionary is required for ON CONFLICT DO UPDATE")

        # Build SET clause
        set_clauses = []
        for key, value in set_.items():
            if hasattr(value, '__clause_element__'):
                set_clauses.append(f"{key} = {value}")
            else:
                set_clauses.append(f"{key} = EXCLUDED.{key}")

        conflict_clause = f"ON CONFLICT DO UPDATE SET {', '.join(set_clauses)}"
        if where is not None:
            conflict_clause += f" WHERE {where}"

        self._post_values_clause = sql.ClauseElement._construct_raw_text(conflict_clause)
        return self

# Alias for backward compatibility
insert = DuckDBInsert


class Dialect(DefaultDialect):
    """DuckDB SQLAlchemy dialect"""
    name = "duckdb"
    driver = "duckdb_engine"

    # DuckDB capabilities
    supports_alter = True
    supports_unicode_binds = True
    supports_sane_rowcount = False
    supports_statement_cache = False
    supports_comments = has_comment_support()
    supports_server_side_cursors = False
    supports_schemas = True
    supports_views = True
    supports_empty_insert = False
    supports_multivalues_insert = True

    # DuckDB doesn't support traditional sequences
    supports_sequences = False

    # DuckDB uses / for division, not integer division like PostgreSQL
    div_is_floordiv = False

    # Set up components
    inspector = DuckDBInspector
    preparer = DuckDBIdentifierPreparer
    type_compiler = DuckDBTypeCompiler
    statement_compiler = DuckDBCompiler
    ddl_compiler = DuckDBDDLCompiler

    # Type mappings
    colspecs = {
        sqltypes.Numeric: sqltypes.Numeric,
        sqltypes.JSON: sqltypes.JSON,
    }

    ischema_names = ISCHEMA_NAMES.copy()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def type_descriptor(self, typeobj: Type[sqltypes.TypeEngine]) -> Any:
        """Get type descriptor for given type"""
        if isinstance(typeobj, type):
            typeobj = typeobj()

        if isinstance(typeobj, sqltypes.NullType):
            return DuckDBNullType()

        return typeobj


    def connect(self, *cargs: Any, **cparams: Any) -> "Connection":
        """Create DuckDB connection with DuckDB-specific parameters"""
        core_keys = get_core_config()
        preload_extensions = cparams.pop("preload_extensions", [])
        config = dict(cparams.get("config", {}))
        cparams["config"] = config
        config.update(cparams.pop("url_config", {}))

        ext = {k: config.pop(k) for k in list(config) if k not in core_keys}

        if supports_user_agent:
            user_agent = f"duckdb_engine/{__version__}(sqlalchemy/{sqlalchemy_version})"
            if "custom_user_agent" in config:
                user_agent = f"{user_agent} {config['custom_user_agent']}"
            config["custom_user_agent"] = user_agent

        filesystems = cparams.pop("register_filesystems", [])

        conn = duckdb.connect(*cargs, **cparams)

        for extension in preload_extensions:
            conn.execute(f"LOAD {extension}")

        for filesystem in filesystems:
            conn.register_filesystem(filesystem)

        apply_config(self, conn, ext)

        return ConnectionWrapper(conn)

    def on_connect(self) -> None:
        """Called once per connection"""
        pass

    @classmethod
    def get_pool_class(cls, url: URL) -> Type[pool.Pool]:
        """Return appropriate connection pool class"""
        if url.database == ":memory:":
            return pool.SingletonThreadPool
        else:
            return pool.QueuePool

    @staticmethod
    def dbapi(**kwargs: Any) -> Any:
        """Return the DBAPI module"""
        return duckdb

    def _get_server_version_info(self, connection: "Connection") -> Tuple[int, int]:
        """Return server version info"""
        # DuckDB doesn't have traditional server versions like PostgreSQL
        return (1, 0)

    def get_default_isolation_level(self, connection: "Connection") -> None:
        """DuckDB doesn't support isolation levels"""
        return None

    def do_rollback(self, connection: "Connection") -> None:
        """Handle rollback with DuckDB-specific error handling"""
        try:
            connection.rollback()
        except duckdb.TransactionException as e:
            if (
                e.args[0]
                != "TransactionContext Error: cannot rollback - no transaction is active"
            ):
                raise e

    def do_begin(self, connection: "Connection") -> None:
        """Begin transaction"""
        connection.begin()

    def has_table(
        self,
        connection: "Connection",
        table_name: str,
        schema: Optional[str] = None,
        **kw: Any,
    ) -> bool:
        """Check if table exists"""
        try:
            self.get_table_oid(connection, table_name, schema)
            return True
        except NoSuchTableError:
            return False

    def get_table_oid(
        self,
        connection: "Connection",
        table_name: str,
        schema: Optional[str] = None,
        **kw: Any,
    ) -> int:
        """Get table OID"""
        if not supports_attach:
            # Simple check for older DuckDB versions
            query = """
                SELECT 1 FROM information_schema.tables
                WHERE table_name = :table_name
            """
            params = {"table_name": table_name}
            if schema:
                query += " AND table_schema = :schema"
                params["schema"] = schema

            result = connection.execute(text(query), params).scalar()
            if result is None:
                raise NoSuchTableError(table_name)
            return 1

        query = """
            SELECT table_oid, table_name
            FROM (
                SELECT table_oid, table_name, database_name, schema_name FROM duckdb_tables()
                UNION ALL BY NAME
                SELECT view_oid AS table_oid, view_name AS table_name, database_name, schema_name FROM duckdb_views()
            )
            WHERE schema_name NOT LIKE 'pg\\_%' ESCAPE '\\'
            AND table_name = :table_name
        """
        params = {"table_name": table_name}

        if schema:
            database_name, schema_name = self.identifier_preparer._separate(schema)
            if schema_name:
                query += " AND schema_name = :schema_name"
                params["schema_name"] = schema_name
            if database_name:
                query += " AND database_name = :database_name"
                params["database_name"] = database_name

        rs = connection.execute(text(query), params)
        table_oid = rs.scalar()
        if table_oid is None:
            raise NoSuchTableError(table_name)
        return table_oid

    def get_indexes(
        self,
        connection: "Connection",
        table_name: str,
        schema: Optional[str] = None,
        **kw: Any,
    ) -> List["_IndexDict"]:
        """DuckDB doesn't support indexes yet"""
        index_warning()
        return []

    def get_multi_indexes(
        self,
        connection: "Connection",
        schema: Optional[str] = None,
        filter_names: Optional[Collection[str]] = None,
        **kw: Any,
    ) -> Iterable[Tuple]:
        """DuckDB doesn't support indexes yet"""
        index_warning()
        return []

    def initialize(self, connection: "Connection") -> None:
        """Initialize dialect"""
        super().initialize(connection)

    def create_connect_args(self, url: URL) -> Tuple[tuple, dict]:
        """Create connection arguments from URL"""
        opts = url.translate_connect_args(database="database")
        opts["url_config"] = dict(url.query)
        user = opts["url_config"].pop("user", None)
        if user is not None:
            opts["database"] += f"?user={user}"
        return (), opts

    @classmethod
    def import_dbapi(cls: Type["Dialect"]) -> Any:
        """Import DBAPI module"""
        return cls.dbapi()

    def do_executemany(
        self, cursor: Any, statement: Any, parameters: Any, context: Optional[Any] = None
    ) -> None:
        """Execute many statements"""
        cursor.executemany(statement, parameters)


# Custom compilation for DuckDB INSERT
@compiles(DuckDBInsert, "duckdb")
def visit_duckdb_insert(element, compiler, **kw):
    """Compile DuckDB INSERT with ON CONFLICT support"""
    # Use standard INSERT compilation and add our post-values clause
    text = compiler.visit_insert(element, **kw)

    if hasattr(element, '_post_values_clause') and element._post_values_clause:
        text += " " + str(element._post_values_clause)

    return text


# Try cast support for DuckDB
class TryCast(sql.ColumnElement):
    """TRY_CAST expression for DuckDB"""
    type = sqltypes.String()
    cache_ok = True

    def __init__(self, expression, target_type):
        self.expression = expression
        self.target_type = target_type


@compiles(TryCast, "duckdb")
def visit_try_cast(element, compiler, **kw):
    """Compile TRY_CAST for DuckDB"""
    return f"TRY_CAST({compiler.process(element.expression, **kw)} AS {element.target_type})"