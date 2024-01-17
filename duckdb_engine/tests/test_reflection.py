from pathlib import Path

from sqlalchemy import select, table
from sqlalchemy.engine import Engine

path = Path(__file__).parent / "simple.parquet"


def test_reflection(engine: Engine) -> None:
    users_table = table(str(path))
    users = select(users_table).add_columns("*")
    assert str(users).startswith("SELECT *")

    with engine.connect() as conn:
        conn.execute(users)
