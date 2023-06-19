import duckdb
import pandas as pd
from pytest import mark, raises
from sqlalchemy import text
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.exc import ProgrammingError


def test_integration(engine: Engine) -> None:
    with engine.connect() as conn:
        execute = (
            conn.exec_driver_sql if hasattr(conn, "exec_driver_sql") else conn.execute
        )
        params = ("test_df", pd.DataFrame([{"a": 1}]))
        execute("register", params)  # type: ignore[operator]

        conn.execute(text("select * from test_df"))


@mark.remote_data
@mark.skipif(
    "dev" in duckdb.__version__, reason="md extension not available for dev builds"  # type: ignore[attr-defined]
)
def test_motherduck() -> None:
    engine = create_engine("duckdb:///md:motherdb?motherduck_token=motherduckdb_token")

    with raises(
        ProgrammingError,
        match="Jwt is not in the form of Header.Payload.Signature with two dots and 3 sections",
    ):
        engine.connect()
