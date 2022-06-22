from typing import Any, Callable, TypeVar

import duckdb
import pytest
from packaging.specifiers import SpecifierSet
from pytest import fixture, mark
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from typing_extensions import Protocol

pytest.register_assert_rewrite("sqlalchemy.testing.assertions")
FuncT = TypeVar("FuncT", bound=Callable[..., Any])


@fixture
def engine() -> Engine:
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
        return mark.xfail(
            not has_version,
            reason=f"{library} version not desired - desired {specifiers}, found {installed}",
        )(func)

    installed = library.__version__
    has_version = SpecifierSet(specifiers).contains(installed, prereleases=True)

    return decorator


def duckdb_version(specifiers: str) -> Callable[[FuncT], FuncT]:
    "Specify which versions of duckdb a test should run against"
    return library_version(duckdb, specifiers)
