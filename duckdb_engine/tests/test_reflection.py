from pathlib import Path

from snapshottest.module import SnapshotTest
from sqlalchemy import select, table
from sqlalchemy.engine import Engine

path = Path(__file__).parent / "simple.parquet"


def test_reflection(engine: Engine, snapshot: SnapshotTest) -> None:
    users_table = table(str(path))
    users = select(users_table).add_columns("*")
    assert str(users).startswith("SELECT *")

    with engine.connect() as conn:
        res = conn.execute(users).fetchall()
        snapshot.assert_match(res)
