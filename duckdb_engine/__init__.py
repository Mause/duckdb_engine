import re
from dataclasses import dataclass, field
from typing import List

import duckdb
from sqlalchemy.dialects.postgresql import dialect as postgres_dialect


class DBAPI:
    paramstyle = "qmark"

    class Error(Exception):
        pass


DNE = re.compile(r"Catalog: ([^ ]+) with name ([^ ]+) does not exist!")


@dataclass
class ConnectionWrapper:
    c: duckdb.DuckDBPyConnection
    description: List[str] = field(default_factory=list)
    notices: List[str] = field(default_factory=list)

    def cursor(self):
        return self

    @property
    def connection(self):
        return self

    def close(self):
        pass

    @property
    def rowcount(self):
        return self.c.rowcount

    def execute(self, statement, parameters, context):
        self.c.execute(statement, parameters)
        if context.result_column_struct:
            self.description = context.result_column_struct[0]
        else:
            self.description = []

    def fetchone(self):
        self.description = [(None, None)]
        return self.c.fetchone()

    def fetchall(self):
        return self.c.fetchall()

    def commit(self):
        self.c.commit()


class Dialect(postgres_dialect):
    _has_events = False
    identifier_preparer = None

    def connect(self, *args, **kwargs):
        return ConnectionWrapper(duckdb.connect(*args, **kwargs))

    def on_connect(self):
        pass

    def statement_compiler(self, *args, **kwargs):
        # TODO: enforce no `serial` type
        return postgres_dialect.statement_compiler(*args, **kwargs)

    def do_execute(self, cursor, statement, parameters, context):
        if "FOREIGN" in statement:
            # TODO: implement this in the compiler instead
            # doesn't support foreign key constraints
            statement = statement.strip().splitlines()
            statement = [line for line in statement if "FOREIGN" not in line]
            statement[-2] = statement[-2].strip().strip(",")
            statement = "\n".join(statement)

        cursor.execute(statement, parameters, context)

    def has_table(self, connection, table_name, schema=None):
        return False

    def has_sequence(self, connection, sequence_name, schema=None):
        return False

    def has_type(self, connection, type_name, schema=None):
        return False

    @staticmethod
    def dbapi():
        return DBAPI

    def create_connect_args(self, u):
        return (), {"database": u.__to_string__(hide_password=False).split("///")[1]}

    def initialize(self, connection):
        pass

    def do_rollback(self, connection):
        pass

    @classmethod
    def get_dialect_cls(cls, u):
        return cls


dialect = Dialect
