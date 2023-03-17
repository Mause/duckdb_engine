from typing import List

from hypothesis import given, strategies
from hypothesis_sqlalchemy import scheme
from hypothesis_sqlalchemy.sample import table_records, table_records_lists
from sqlalchemy.schema import Column, MetaData, Table
from sqlalchemy.sql.sqltypes import Integer, String

from .. import Dialect

dialect = Dialect()
tables = scheme.tables(dialect, min_size=3, max_size=10)


@given(tables)
def test_hypo_table(table: Table) -> None:
    assert isinstance(table, Table)
    assert all(isinstance(column, Column) for column in table.columns)
    assert 3 <= len(table.columns) <= 10


metadata = MetaData()
user_table = Table(
    "user",
    metadata,
    Column("user_id", Integer, primary_key=True),
    Column("user_name", String(16), nullable=False),
    Column("email_address", String(60)),
    Column("password", String(20), nullable=False),
)


records = table_records(user_table, email_address=strategies.emails())


@given(records)
def test_hypo_record(record: tuple) -> None:
    assert isinstance(record, tuple)
    assert len(record) == len(user_table.columns)
    assert all(
        column.nullable and value is None or isinstance(value, column.type.python_type)
        for value, column in zip(record, user_table.columns)
    )


records_lists = table_records_lists(
    user_table, min_size=2, max_size=5, email_address=strategies.emails()
)


@given(records_lists)
def test_hypo_records(records_list: List[tuple]) -> None:
    assert isinstance(records_list, list)
    assert 2 <= len(records_list) <= 5
    assert all(isinstance(record, tuple) for record in records_list)
    assert all(len(record) == len(user_table.columns) for record in records_list)
