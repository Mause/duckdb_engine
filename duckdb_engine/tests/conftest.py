from functools import wraps
from typing import Any, Callable, TypeVar, cast

import duckdb
from packaging.specifiers import SpecifierSet
from pytest import fixture, xfail
from sqlalchemy import create_engine
from sqlalchemy.dialects import registry
from sqlalchemy.engine import Engine

T = TypeVar("T")
FuncT = TypeVar("FuncT", bound=Callable[..., Any])


@fixture
def engine() -> Engine:
    registry.register("duckdb", "duckdb_engine", "Dialect")  # type: ignore

    return create_engine("duckdb:///:memory:")


def duckdb_version(
    specifiers: str,
) -> Callable[[FuncT], FuncT]:
    """
    Specify which version of duckdb a test should run against
    """

    def decorator(func: FuncT) -> FuncT:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            if not has_version:
                xfail(
                    f"duckdb version not desired - desired {specifiers}, found {installed}"
                )

            return func(*args, **kwargs)

        return cast(FuncT, wrapper)

    installed = duckdb.__version__
    has_version = SpecifierSet(specifiers).contains(installed, prereleases=True)

    return decorator
