from typing import Any, Callable, Protocol, TypeVar

import duckdb
from packaging.specifiers import SpecifierSet
from pytest import fixture, mark
from sqlalchemy import create_engine
from sqlalchemy.dialects import registry
from sqlalchemy.engine import Engine

FuncT = TypeVar("FuncT", bound=Callable[..., Any])


@fixture
def engine() -> Engine:
    registry.register("duckdb", "duckdb_engine", "Dialect")  # type: ignore

    return create_engine("duckdb:///:memory:")


class HasVersion(Protocol):
    __version__: str


def library_version(
    library: HasVersion,
    specifiers: str,
) -> Callable[[FuncT], FuncT]:
    """
    Specify which versions of a library a test should run against
    """

    def decorator(func: FuncT) -> FuncT:
        if not has_version:
            func = mark.xfail(
                f"{library} version not desired - desired {specifiers}, found {installed}"
            )(func)

        return func

    installed = library.__version__
    has_version = SpecifierSet(specifiers).contains(installed, prereleases=True)

    return decorator


def duckdb_version(specifiers: str) -> Callable[[FuncT], FuncT]:
    "Specify which versions of duckdb a test should run against"
    return library_version(duckdb, specifiers)
