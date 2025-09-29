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
from sqlalchemy.engine import default
from sqlalchemy.engine.default import DefaultDialect
from sqlalchemy.engine.interfaces import Dialect as RootDialect
from sqlalchemy.engine.reflection import Inspector, cache
from sqlalchemy.engine.url import URL
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.schema import Sequence
from sqlalchemy.sql import bindparam, compiler
from sqlalchemy.sql.compiler import IdentifierPreparer
from sqlalchemy.sql.dml import Insert
from sqlalchemy.sql.selectable import Select

from ._supports import has_comment_support
from .config import apply_config, get_core_config
from .datatypes import ISCHEMA_NAMES, register_extension_types

__version__ = "0.17.0"
sqlalchemy_version = sqlalchemy.__version__
duckdb_version: str = duckdb.__version__
supports_attach: bool = duckdb_version >= "0.7.0"
supports_user_agent: bool = duckdb_version >= "0.9.2"

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection
    from sqlalchemy.engine.interfaces import ReflectedIndex as _IndexDict
    from sqlalchemy.sql.type_api import _ResultProcessorType as _ResultProcessor

register_extension_types()


__all__ = [
    "Dialect",
    "ConnectionWrapper",
    "CursorWrapper",
    "DuckDBEngineWarning",
    "DuckDBInsert",
    "insert",
]


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
        if not hasattr(self.__c, "description") or self.__c.description is None:
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


class DuckDBBLOB(sqltypes.BLOB):
    """DuckDB-specific BLOB type that doesn't require Binary attribute"""

    def bind_processor(self, dialect):
        """Process bound parameters for BLOB columns"""
        # DuckDB handles bytes directly without needing a Binary wrapper
        return lambda value: value if value is not None else None

    def result_processor(self, dialect, coltype):
        """Process result values for BLOB columns"""
        return lambda value: value if value is not None else None


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

    def visit_BLOB(self, type_: sqltypes.BLOB, **kw: Any) -> str:
        return "BLOB"

    def visit_datetime(self, type_: sqltypes.DateTime, **kw: Any) -> str:
        return "TIMESTAMP"

    def visit_DATETIME(self, type_: sqltypes.DATETIME, **kw: Any) -> str:
        return "TIMESTAMP"


class DuckDBExecutionContext(default.DefaultExecutionContext):
    """DuckDB execution context with sequence support"""

    def fire_sequence(self, seq, type_):
        """Execute a sequence to get the next value"""
        # Use SELECT nextval() to get the next sequence value
        result = self._execute_scalar(f"SELECT nextval('{seq.name}')", None)
        return result


class DuckDBCompiler(compiler.SQLCompiler):
    """DuckDB SQL compiler"""

    def visit_try_cast(self, element, **kw):
        """Compile TryCast to DuckDB's TRY_CAST syntax"""
        return f"TRY_CAST({self.process(element.clause, **kw)} AS {self.process(element.type, **kw)})"

    def visit_datetime(self, type_, **kw):
        """Compile DateTime type references"""
        return self.dialect.type_compiler.visit_datetime(type_, **kw)

    def visit_sequence(self, sequence, **kw):
        """Compile sequence references to nextval() calls"""
        return f"nextval('{sequence.name}')"

    def visit_function(self, func, **kw):
        """Compile SQL functions with DuckDB-specific handling"""
        # Handle date_part function specifically
        if hasattr(func, "name") and func.name.lower() == "date_part":
            # DuckDB uses date_part(part, date) syntax
            if len(func.clauses) == 2:
                # For date_part, inline string literals to avoid DuckDB GROUP BY issues
                part_clause = func.clauses.clauses[0]
                if hasattr(part_clause, "value") and isinstance(part_clause.value, str):
                    # Inline the string literal instead of using parameters
                    part = f"'{part_clause.value}'"
                else:
                    part = self.process(func.clauses.clauses[0], **kw)
                date_expr = self.process(func.clauses.clauses[1], **kw)
                return f"date_part({part}, {date_expr})"

        # Handle extract function - convert to date_part
        if hasattr(func, "name") and func.name.lower() == "extract":
            if len(func.clauses) == 2:
                part_clause = func.clauses.clauses[0]
                if hasattr(part_clause, "value") and isinstance(part_clause.value, str):
                    # Inline the string literal instead of using parameters
                    part = f"'{part_clause.value}'"
                else:
                    part = self.process(func.clauses.clauses[0], **kw)
                date_expr = self.process(func.clauses.clauses[1], **kw)
                return f"date_part({part}, {date_expr})"

        # For all other functions, use default SQLAlchemy compilation
        return super().visit_function(func, **kw)


class DuckDBDDLCompiler(compiler.DDLCompiler):
    """DuckDB DDL compiler"""

    def get_column_specification(self, column, **kwargs):
        """Override to handle DuckDB-specific column specs"""
        spec = super().get_column_specification(column, **kwargs)
        return spec

    def get_column_default_string(self, column):
        """Override to handle sequence defaults for DuckDB"""
        if column.default and isinstance(column.default, Sequence):
            # Handle Sequence objects attached to column.default
            seq_name = column.default.name
            return f"nextval('{seq_name}')"
        elif (
            column.server_default
            and hasattr(column.server_default, "arg")
            and isinstance(column.server_default.arg, Sequence)
        ):
            # Handle Sequence objects attached to column.server_default
            seq_name = column.server_default.arg.name
            return f"nextval('{seq_name}')"
        return super().get_column_default_string(column)


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

    @property
    def excluded(self):
        """Return the EXCLUDED pseudo-table for use in ON CONFLICT DO UPDATE"""
        from sqlalchemy import column, table

        # Create a pseudo-table representing the EXCLUDED values
        cols = [column(c.key) for c in self.table.columns]
        excluded_table = table("excluded", *cols)
        return excluded_table

    def on_conflict_do_nothing(self, constraint=None):
        """Add ON CONFLICT DO NOTHING clause"""
        self._post_values_clause = text("ON CONFLICT DO NOTHING")
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

        # Build conflict target
        conflict_target = ""
        if index_elements:
            # Convert column objects to column names
            column_names = []
            for elem in index_elements:
                if hasattr(elem, "name"):
                    column_names.append(elem.name)
                elif hasattr(elem, "key"):
                    column_names.append(elem.key)
                else:
                    column_names.append(str(elem))
            conflict_target = f"({', '.join(column_names)})"

        # Build SET clause
        set_clauses = []
        for key, value in set_.items():
            if hasattr(value, "_compiler_dispatch"):
                # This is a column expression - for now, we'll handle excluded references manually
                if (
                    hasattr(value, "table")
                    and hasattr(value.table, "name")
                    and value.table.name == "excluded"
                ):
                    set_clauses.append(f"{key} = EXCLUDED.{value.name}")
                else:
                    # Other expressions would need compilation
                    set_clauses.append(f"{key} = EXCLUDED.{key}")
            else:
                # Direct value or string reference
                set_clauses.append(f"{key} = EXCLUDED.{key}")

        conflict_clause = (
            f"ON CONFLICT {conflict_target} DO UPDATE SET {', '.join(set_clauses)}"
        )
        if where is not None:
            conflict_clause += f" WHERE {where}"

        self._post_values_clause = text(conflict_clause)
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

    # DuckDB supports sequences
    supports_sequences = True

    # DuckDB uses / for division, not integer division like PostgreSQL
    div_is_floordiv = False

    # Set up components
    preparer = DuckDBIdentifierPreparer
    type_compiler = DuckDBTypeCompiler
    statement_compiler = DuckDBCompiler
    ddl_compiler = DuckDBDDLCompiler
    execution_ctx_cls = DuckDBExecutionContext

    # Type mappings
    colspecs = {
        sqltypes.Numeric: sqltypes.Numeric,
        sqltypes.JSON: sqltypes.JSON,
        sqltypes.BLOB: DuckDBBLOB,
    }

    ischema_names = ISCHEMA_NAMES.copy()

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        # Extract JSON serialization parameters before calling super()
        self._json_serializer = kwargs.pop("json_serializer", None)
        self._json_deserializer = kwargs.pop("json_deserializer", None)

        super().__init__(*args, **kwargs)
        # Add Binary attribute to duckdb module for BLOB compatibility
        if not hasattr(duckdb, "Binary"):
            duckdb.Binary = lambda x: x  # Simple identity function

    def type_descriptor(self, typeobj: Type[sqltypes.TypeEngine]) -> Any:
        """Get type descriptor for given type"""
        if isinstance(typeobj, type):
            typeobj = typeobj()

        if isinstance(typeobj, sqltypes.NullType):
            return DuckDBNullType()

        return typeobj

    def _json_serializer_fn(self, value):
        """Default JSON serializer if none provided"""
        if self._json_serializer is not None:
            return self._json_serializer(value)
        import json

        return json.dumps(value)

    def _json_deserializer_fn(self, value):
        """Default JSON deserializer if none provided"""
        if self._json_deserializer is not None:
            return self._json_deserializer(value)
        import json

        return json.loads(value)

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

    def has_sequence(
        self,
        connection,
        sequence_name: str,
        schema: Optional[str] = None,
        **kw: Any,
    ) -> bool:
        """Check if a sequence exists in DuckDB"""
        query = """
            SELECT COUNT(*) FROM duckdb_sequences() WHERE sequence_name = :seq_name
        """

        params = {"seq_name": sequence_name}
        if schema:
            # DuckDB sequences include schema info in the sequence name or separate field
            # For now, just check by name - this could be improved
            pass

        result = connection.execute(text(query), params)
        return bool(result.scalar())

    def fire_sequence(self, seq, type_):
        """Execute a sequence to get the next value"""
        # This method shouldn't be called with our custom execution context
        # But if it is, we need to handle it properly
        raise NotImplementedError(
            "Sequence execution should be handled by DuckDBExecutionContext"
        )

    def get_view_names(
        self, connection, schema: Optional[str] = None, **kw: Any
    ) -> List[str]:
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
                rs = connection.execute(text(query), {"schema": schema})
                return [view for (view,) in rs]
            else:
                query += " AND table_schema = 'main'"  # Only return main schema views by default
                rs = connection.execute(text(query))
                return [view for (view,) in rs]

        query = """
            SELECT view_name
            FROM duckdb_views()
            WHERE internal = false
        """
        params = {}

        if schema:
            database_name, schema_name = self.identifier_preparer._separate(schema)
            if schema_name:
                query += " AND schema_name = :schema_name"
                params["schema_name"] = schema_name
            if database_name:
                query += " AND database_name = :database_name"
                params["database_name"] = database_name
        else:
            # Default to main schema only
            query += " AND schema_name = 'main' AND database_name = 'memory'"

        rs = connection.execute(text(query), params)
        return [view for (view,) in rs]

    def get_schema_names(self, connection, **kw: Any) -> List[str]:
        """Return list of schema names using duckdb_schemas()"""
        if not supports_attach:
            # Fallback for older DuckDB versions
            return ["main"]

        query = """
            SELECT database_name, schema_name
            FROM duckdb_schemas()
            WHERE schema_name != 'pg_catalog'
            ORDER BY database_name, schema_name
        """
        rs = connection.execute(text(query))
        return [self.identifier_preparer.quote_schema(".".join(row)) for row in rs]

    def get_table_names(
        self, connection, schema: Optional[str] = None, **kw: Any
    ) -> List[str]:
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
                rs = connection.execute(text(query), {"schema": schema})
                return [table for (table,) in rs]
            else:
                query += " AND table_schema = 'main'"  # Only return main schema tables by default
                rs = connection.execute(text(query))
                return [table for (table,) in rs]

        query = """
            SELECT table_name
            FROM duckdb_tables()
            WHERE internal = false
        """
        params = {}

        if schema:
            database_name, schema_name = self.identifier_preparer._separate(schema)
            if schema_name:
                query += " AND schema_name = :schema_name"
                params["schema_name"] = schema_name
            if database_name:
                query += " AND database_name = :database_name"
                params["database_name"] = database_name
        else:
            # For default case, don't restrict by schema/database to get all tables
            pass

        rs = connection.execute(text(query), params)
        return [table for (table,) in rs]

    def get_table_comment(
        self, connection, table_name: str, schema: Optional[str] = None, **kw: Any
    ) -> Dict[str, Optional[str]]:
        """Return table comment"""
        # DuckDB doesn't have built-in table comments in older versions
        # But we can check if comment support is available
        if not self.supports_comments:
            return {"text": None}

        # For newer DuckDB versions with comment support
        try:
            # Use duckdb_tables() function which has proper comment support
            query = """
                SELECT comment
                FROM duckdb_tables()
                WHERE table_name = :table_name
            """
            params = {"table_name": table_name}

            if schema:
                query += " AND schema_name = :schema"
                params["schema"] = schema
            else:
                # Default to main schema if not specified
                query += " AND schema_name = 'main'"

            result = connection.execute(text(query), params).scalar()
            return {"text": result}
        except Exception:
            # Fallback: try information_schema.tables with TABLE_COMMENT column
            try:
                query = """
                    SELECT TABLE_COMMENT
                    FROM information_schema.tables
                    WHERE table_name = :table_name
                """
                params = {"table_name": table_name}

                if schema:
                    query += " AND table_schema = :schema"
                    params["schema"] = schema

                result = connection.execute(text(query), params).scalar()
                return {"text": result}
            except Exception:
                # Final fallback if comment support isn't available
                return {"text": None}

    def get_columns(
        self,
        connection,
        table_name: str,
        schema: Optional[str] = None,
        **kw: Any,
    ):
        """Return information about columns in table_name"""

        # If comment support is available, use duckdb_columns() for richer information
        if self.supports_comments:
            try:
                query = """
                    SELECT
                        column_name,
                        data_type,
                        is_nullable,
                        column_default,
                        comment
                    FROM duckdb_columns()
                    WHERE table_name = :table_name
                """
                params = {"table_name": table_name}

                if schema:
                    database_name, schema_name = self.identifier_preparer._separate(
                        schema
                    )
                    if schema_name:
                        query += " AND schema_name = :schema_name"
                        params["schema_name"] = schema_name
                    if database_name:
                        query += " AND database_name = :database_name"
                        params["database_name"] = database_name
                else:
                    # When no schema is specified, search all schemas for the table
                    pass

                query += " ORDER BY column_index"

                result = connection.execute(text(query), params)
                columns = []

                for row in result:
                    col_name, data_type, is_nullable, column_default, comment = row

                    # Convert DuckDB types to SQLAlchemy types
                    type_obj = self._map_duckdb_type_to_sqlalchemy(data_type)

                    columns.append(
                        {
                            "name": col_name,
                            "type": type_obj,
                            "nullable": is_nullable,
                            "default": column_default,
                            "comment": comment,
                        }
                    )

                return columns
            except Exception:
                # Fall back to information_schema if duckdb_columns() fails
                pass

        # Fallback: use information_schema.columns (no comment support)
        query = """
            SELECT
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = :table_name
        """
        params = {"table_name": table_name}

        if schema:
            database_name, schema_name = self.identifier_preparer._separate(schema)
            if schema_name:
                query += " AND table_schema = :schema_name"
                params["schema_name"] = schema_name
            # Note: information_schema doesn't have database_name, so we ignore it here
        else:
            # When no schema is specified, search all schemas for the table
            pass

        query += " ORDER BY ordinal_position"

        result = connection.execute(text(query), params)
        columns = []

        for row in result:
            col_name, data_type, is_nullable, column_default = row

            # Convert DuckDB types to SQLAlchemy types
            type_obj = self._map_duckdb_type_to_sqlalchemy(data_type)

            columns.append(
                {
                    "name": col_name,
                    "type": type_obj,
                    "nullable": is_nullable.upper() == "YES",
                    "default": column_default,
                }
            )

        return columns

    def _map_duckdb_type_to_sqlalchemy(self, data_type: str):
        """Map DuckDB data type to SQLAlchemy type"""
        # Handle complex types that should be mapped to NULLTYPE
        if (
            "[" in data_type  # Arrays like INTEGER[] or INTEGER[3]
            or "STRUCT(" in data_type  # Structs like STRUCT(a INTEGER, b VARCHAR)
            or "MAP(" in data_type  # Maps like MAP(VARCHAR, VARCHAR)
            or "UNION(" in data_type  # Unions
        ):
            return sqltypes.NULLTYPE

        # For basic types, use the existing mapping
        return self.ischema_names.get(data_type.upper(), sqltypes.String)()

    def get_foreign_keys(
        self,
        connection,
        table_name: str,
        schema: Optional[str] = None,
        **kw: Any,
    ):
        """Return information about foreign keys in table_name"""
        query = """
            SELECT
                constraint_index,
                constraint_text,
                constraint_column_names,
                referenced_table,
                referenced_column_names
            FROM duckdb_constraints()
            WHERE constraint_type = 'FOREIGN KEY'
                AND table_name = :table_name
        """
        params = {"table_name": table_name}

        if schema:
            query += " AND schema_name = :schema"
            params["schema"] = schema

        result = connection.execute(text(query), params)
        foreign_keys = []

        # Group by constraint_index to handle multi-column foreign keys
        fk_dict = {}
        for row in result:
            constraint_idx = row.constraint_index
            constraint_text = row.constraint_text
            constrained_cols = row.constraint_column_names or []
            referenced_table = row.referenced_table
            referenced_cols = row.referenced_column_names or []

            # Extract constraint name from constraint_text if available
            constraint_name = None
            if constraint_text:
                # Try to extract name from "CONSTRAINT name FOREIGN KEY..."
                import re

                match = re.search(
                    r"CONSTRAINT\s+(\w+)\s+FOREIGN\s+KEY",
                    constraint_text,
                    re.IGNORECASE,
                )
                if match:
                    constraint_name = match.group(1)

            if constraint_idx not in fk_dict:
                fk_dict[constraint_idx] = {
                    "name": constraint_name,
                    "constrained_columns": constrained_cols,
                    "referred_schema": schema,
                    "referred_table": referenced_table,
                    "referred_columns": referenced_cols,
                }

        foreign_keys = list(fk_dict.values())
        return foreign_keys

    def get_check_constraints(
        self,
        connection,
        table_name: str,
        schema: Optional[str] = None,
        **kw: Any,
    ):
        """Return information about check constraints in table_name"""
        query = """
            SELECT
                constraint_index,
                constraint_text,
                constraint_column_names
            FROM duckdb_constraints()
            WHERE constraint_type = 'CHECK'
                AND table_name = :table_name
        """
        params = {"table_name": table_name}

        if schema:
            query += " AND schema_name = :schema"
            params["schema"] = schema

        result = connection.execute(text(query), params)
        check_constraints = []

        for row in result:
            constraint_text = row.constraint_text
            constraint_cols = row.constraint_column_names or []

            # Extract constraint name and SQL text from constraint_text
            constraint_name = None
            sqltext = constraint_text

            if constraint_text:
                import re

                # Try to extract name from "CONSTRAINT name CHECK (condition)"
                match = re.search(
                    r"CONSTRAINT\s+(\w+)\s+CHECK\s*\((.*)\)",
                    constraint_text,
                    re.IGNORECASE | re.DOTALL,
                )
                if match:
                    constraint_name = match.group(1)
                    sqltext = match.group(2).strip()
                else:
                    # Try to extract just the CHECK condition
                    match = re.search(
                        r"CHECK\s*\((.*)\)", constraint_text, re.IGNORECASE | re.DOTALL
                    )
                    if match:
                        sqltext = match.group(1).strip()

            check_constraints.append(
                {
                    "name": constraint_name,
                    "sqltext": sqltext,
                    "dialect_options": {},
                    "comment": None,
                }
            )

        return check_constraints

    def get_unique_constraints(
        self,
        connection,
        table_name: str,
        schema: Optional[str] = None,
        **kw: Any,
    ):
        """Return information about unique constraints in table_name"""
        query = """
            SELECT
                constraint_index,
                constraint_text,
                constraint_column_names
            FROM duckdb_constraints()
            WHERE constraint_type = 'UNIQUE'
                AND table_name = :table_name
        """
        params = {"table_name": table_name}

        if schema:
            query += " AND schema_name = :schema"
            params["schema"] = schema

        result = connection.execute(text(query), params)
        unique_constraints = []

        for row in result:
            constraint_text = row.constraint_text
            constraint_cols = row.constraint_column_names or []

            # Extract constraint name from constraint_text
            constraint_name = None
            if constraint_text:
                import re

                # Try to extract name from "CONSTRAINT name UNIQUE (cols)"
                match = re.search(
                    r"CONSTRAINT\s+(\w+)\s+UNIQUE", constraint_text, re.IGNORECASE
                )
                if match:
                    constraint_name = match.group(1)

            unique_constraints.append(
                {
                    "name": constraint_name,
                    "column_names": constraint_cols,
                    "duplicates_index": False,
                    "dialect_options": {},
                    "comment": None,
                }
            )

        return unique_constraints

    def get_pk_constraint(
        self,
        connection,
        table_name: str,
        schema: Optional[str] = None,
        **kw: Any,
    ):
        """Return information about primary key constraint in table_name"""
        query = """
            SELECT
                constraint_index,
                constraint_text,
                constraint_column_names
            FROM duckdb_constraints()
            WHERE constraint_type = 'PRIMARY KEY'
                AND table_name = :table_name
        """
        params = {"table_name": table_name}

        if schema:
            query += " AND schema_name = :schema"
            params["schema"] = schema

        result = connection.execute(text(query), params)

        # There should be at most one primary key constraint per table
        for row in result:
            constraint_text = row.constraint_text
            constraint_cols = row.constraint_column_names or []

            # Extract constraint name from constraint_text
            constraint_name = None
            if constraint_text:
                import re

                # Try to extract name from "CONSTRAINT name PRIMARY KEY (cols)"
                match = re.search(
                    r"CONSTRAINT\s+(\w+)\s+PRIMARY\s+KEY",
                    constraint_text,
                    re.IGNORECASE,
                )
                if match:
                    constraint_name = match.group(1)

            return {
                "constrained_columns": constraint_cols,
                "name": constraint_name,
                "dialect_options": {},
                "comment": None,
            }

        # Return empty constraint if no primary key found
        return {
            "constrained_columns": [],
            "name": None,
            "dialect_options": {},
            "comment": None,
        }

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
        self,
        cursor: Any,
        statement: Any,
        parameters: Any,
        context: Optional[Any] = None,
    ) -> None:
        """Execute many statements"""
        cursor.executemany(statement, parameters)


# Custom compilation for DuckDB INSERT
@compiles(DuckDBInsert, "duckdb")
def visit_duckdb_insert(element, compiler, **kw):
    """Compile DuckDB INSERT with ON CONFLICT support"""
    # Use standard INSERT compilation and add our post-values clause
    text = compiler.visit_insert(element, **kw)

    # Only add the post-values clause if it exists and hasn't been added yet
    if (
        hasattr(element, "_post_values_clause")
        and element._post_values_clause is not None
        and "ON CONFLICT" not in text
    ):  # Avoid duplication
        post_clause = compiler.process(element._post_values_clause, literal_binds=True)
        text += " " + post_clause

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
