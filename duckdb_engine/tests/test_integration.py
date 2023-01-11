import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


def test_integration(engine: Engine) -> None:
    with engine.connect() as conn:
        execute = (
            conn.exec_driver_sql if hasattr(conn, "exec_driver_sql") else conn.execute
        )
        execute("register('test_df', ?)", ((pd.DataFrame([{"a": 1}]),),))  # type: ignore[operator]

        conn.execute(text("select * from test_df"))
