#! /usr/bin/env python3
# vim:fenc=utf-8

"""
Test pandas functionality.
"""

from collections import OrderedDict
from datetime import datetime
from itertools import product
from typing import Optional

import pandas as pd
from pytest import mark
from sqlalchemy import create_engine

_possible_args = OrderedDict(
    {
        "chunksize": [None, 1, 10000],
        "if_exists": ["fail", "replace", "append"],
        "method": [
            None,
            "multi",
        ],  # TODO Implement a callable insert method?
    }
)

args = {
    "to_sql": ["chunksize", "if_exists", "method"],
    "read_sql": ["chunksize"],
}
params = {
    k: list(
        product(*(_v for _k, _v in _possible_args.items() if _k in args[k]))  # type: ignore
    )
    for k in args
}
params_strings = {k: (",".join([str(_k) for _k in args[k]])) for k in args}

sample_df = pd.DataFrame(
    {
        "datetime": [datetime.utcnow()],
        "int": [1],
        "float": [1.01],
        "str": ["foo"],
    }
)


@mark.parametrize(params_strings["to_sql"], params["to_sql"])
def test_to_sql(
    chunksize: Optional[int],
    if_exists: str,
    method: Optional[str],
    index: bool = False,
) -> None:
    eng = create_engine("duckdb:///:memory:")
    try:
        sample_df.to_sql(
            name="foo",
            con=eng,
            if_exists=if_exists,
            chunksize=chunksize,
            index=index,
        )
    except ValueError as e:
        if if_exists != "fail":
            raise e


@mark.parametrize(params_strings["read_sql"], params["read_sql"])
def test_read_sql(
    chunksize: Optional[int],
) -> None:
    eng = create_engine("duckdb:///:memory:")
    sample_df.to_sql(name="test_read", con=eng, if_exists="replace")
    query = "SELECT * FROM test_read"
    result = pd.read_sql(
        query,
        eng,
        chunksize=chunksize,
    )
    chunks = [result] if chunksize is None else [chunk for chunk in result]
    pd.concat(chunks).reset_index(drop=True)
