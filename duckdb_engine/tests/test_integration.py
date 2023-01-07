import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine


def test_integration(engine: Engine) -> None:
    engine.execute(text("register"), ("test_df", pd.DataFrame([{"a": 1}])))

    engine.execute(text("select * from test_df"))
