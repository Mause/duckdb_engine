"""
these are largely just smoke tests
"""

from csv import DictWriter
from pathlib import Path
from typing import TYPE_CHECKING

from pytest import fixture, importorskip

importorskip("ibis")

if TYPE_CHECKING:
    from ibis.backends.duckdb import Backend


@fixture
def ibis_conn() -> "Backend":
    import ibis

    return ibis.duckdb.connect()


def test_csv(tmp_path: Path, ibis_conn: "Backend") -> None:
    path = tmp_path / "test.csv"
    with path.open("w") as fh:
        cfh = DictWriter(fh, ["mean"])
        cfh.writeheader()
        cfh.writerow({"mean": 6})

    ibis_conn.register(f"csv://{path}")


def test_pandas(ibis_conn: "Backend") -> None:
    pandas = importorskip("pandas")
    df = pandas.DataFrame({"mean": [6]})
    ibis_conn.register(df)


def test_method_call(ibis_conn: "Backend") -> None:
    importorskip("pyarrow")
    with ibis_conn._safe_raw_sql("select 1") as cursor:
        cursor.cursor.fetch_record_batch()
