from dataclasses import dataclass, field
from typing import List

import duckdb
from sqlalchemy.dialects.postgresql import dialect as postgres_dialect


class DBAPI:
    paramstyle = "qmark"

    class Error(Exception):
        pass


@dataclass
class ConnectionWrapper:
    c: duckdb.DuckDBPyConnection
    notices: List[str] = field(default_factory=list)

    def cursor(self):
        return self

    def __getattr__(self, name):
        return getattr(self.c, name)

    @property
    def connection(self):
        return self

    def close(self):
        # duckdb doesn't support 'soft closes'
        pass

    def execute(self, statement, parameters, context):
        self.c.execute(statement, parameters)


class Dialect(postgres_dialect):
    _has_events = False
    identifier_preparer = None
    # colspecs TODO: remap types to duckdb types

    def connect(self, *args, **kwargs):
        return ConnectionWrapper(duckdb.connect(*args, **kwargs))

    def on_connect(self):
        pass

    def ddl_compiler(self, dialect, ddl, **kwargs):
        # TODO: enforce no `serial` type

        # duckdb doesn't support foreign key constraints (yet)
        ddl.include_foreign_key_constraints = {}
        return postgres_dialect.ddl_compiler(dialect, ddl, **kwargs)

    def do_execute(self, cursor, statement, parameters, context):
        cursor.execute(statement, parameters, context)

    @staticmethod
    def dbapi():
        return DBAPI

    def create_connect_args(self, u):
        return (), {"database": u.render_as_string(hide_password=False).split("///")[1]}

    def initialize(self, connection):
        pass

    def do_rollback(self, connection):
        pass

    @classmethod
    def get_dialect_cls(cls, u):
        return cls


dialect = Dialect
