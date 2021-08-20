from sqlalchemy.engine import Engine
import pandas as pd


def test_integration(engine: Engine):
  engine.execute("register", pd.DataFrame())
