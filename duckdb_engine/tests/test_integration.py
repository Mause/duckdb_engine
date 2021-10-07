import pandas as pd
from sqlalchemy.engine import Engine


def test_integration(engine: Engine) -> None:
    conn = engine.connect()

    conn.exec_driver_sql("register('test_df', ?)", ((pd.DataFrame([{"a": 1}]),),))

    conn.exec_driver_sql("select * from test_df")
