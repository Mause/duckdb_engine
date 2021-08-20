import pandas as pd
from sqlalchemy.engine import Engine


def test_integration(engine: Engine):
    engine.execute("register", pd.DataFrame())
