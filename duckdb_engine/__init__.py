import re
from dataclasses import dataclass, field
from typing import List

import duckdb
from sqlalchemy.dialects.postgresql import dialect


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


class Dialect(dialect):
    _has_events = False
    identifier_preparer = None

    def connect(self, *args, **kwargs):
        return ConnectionWrapper(duckdb.connect(*args, **kwargs))

    def on_connect(self):
        pass

    def do_execute(self, cursor, statement, parameters, context):
        if "FOREIGN" in statement:
            # doesn't support foreign key constraints
            statement = statement.strip().splitlines()
            statement = [line for line in statement if "FOREIGN" not in line]
            statement[-2] = statement[-2].strip().strip(",")
            statement = "\n".join(statement)

        cursor.execute(statement, parameters, context)

        # if "CREATE SEQUENCE" in statement:
        #     seque = statement.split(" ")[2].strip('"')
        #     print(cursor.execute(f"SELECT nextval('{seque}');", ()).fetchone())

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
