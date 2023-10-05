import duckdb
import pandas as pd
from pytest import importorskip, mark, raises
from sqlalchemy import __version__, text
from sqlalchemy.engine import Engine, create_engine
from sqlalchemy.exc import ProgrammingError


def test_integration(engine: Engine) -> None:
    df = pd.DataFrame([{"a": 1}])
    with engine.connect() as conn:
        if hasattr(conn, "exec_driver_sql"):
            conn.exec_driver_sql("register", ("test_df_driver", df))  # type: ignore[arg-type]
            conn.execute(text("select * from test_df_driver"))

        if __version__.startswith("2."):
            conn.execute(text("register(?, ?)"), ("test_df", df))
        else:
            conn.execute(text("register"), ("test_df", df))
        conn.execute(text("select * from test_df"))


@mark.remote_data
@mark.skipif(
    "dev" in duckdb.__version__, reason="md extension not available for dev builds"  # type: ignore[attr-defined]
)
def test_motherduck() -> None:
    importorskip("duckdb", "0.7.1")

    engine = create_engine(
        "duckdb:///md:motherdb",
        connect_args={"config": {"motherduck_token": "motherduckdb_token"}},
    )

    with raises(
        ProgrammingError,
        match="Jwt is not in the form of Header.Payload.Signature with two dots and 3 sections",
    ):
        engine.connect()
