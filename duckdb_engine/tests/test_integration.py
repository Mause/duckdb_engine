import pandas as pd
from sqlalchemy.engine import Engine


def test_integration(engine: Engine) -> None:
    engine.execute("register", ("test_df", pd.DataFrame([{"a": 1}])))

    engine.execute("select * from test_df")
