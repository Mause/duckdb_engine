from functools import wraps
from typing import Any, Callable, TypeVar

import duckdb
from packaging.specifiers import SpecifierSet
from pytest import fixture, mark, raises
from sqlalchemy import create_engine
from sqlalchemy.dialects import registry  # type: ignore
from sqlalchemy.engine import Engine
from typing_extensions import ParamSpec, Protocol

P = ParamSpec("P")

FuncT = TypeVar("FuncT", bound=Callable[..., Any])


@fixture
def engine() -> Engine:
    registry.register("duckdb", "duckdb_engine", "Dialect")

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


def raises_msg(msg: str) -> Callable[[Callable[P, None]], Callable[P, None]]:
    def decorator(func: Callable[P, None]) -> Callable[P, None]:
        @wraps(func)
        def wrapped_test(*args: P.args, **kwargs: P.kwargs) -> None:
            with raises(RuntimeError, match=msg):
                func(*args, **kwargs)

        return wrapped_test

    return decorator


def duckdb_version(specifiers: str) -> Callable[[FuncT], FuncT]:
    "Specify which versions of duckdb a test should run against"
    return library_version(duckdb, specifiers)
