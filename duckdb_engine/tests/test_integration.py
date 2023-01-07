import pandas as pd
from sqlalchemy import text
from sqlalchemy.engine import Engine

from .util import is_sqlalchemy_1


def test_integration(engine: Engine) -> None:
    with engine.connect() as conn:
        if is_sqlalchemy_1:
            conn.execute(text("register"), ("test_df", pd.DataFrame([{"a": 1}])))
        else:
            conn.execute(
                text("register(:name, :df)"),
                {"name": "test_df", "df": pd.DataFrame([{"a": 1}])},
            )

        conn.execute(text("select * from test_df"))
