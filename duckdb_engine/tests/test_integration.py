import pandas as pd
from sqlalchemy.engine import Engine


def test_integration(engine: Engine):
    engine.execute("register", ("test_df", pd.DataFrame()))

    engine.execute("select * from test_df")
