import logging
import os
import sys
import warnings
from functools import wraps
from subprocess import check_call
from typing import Any, Callable, Generator, TypeVar

from pytest import fixture, raises
from sqlalchemy import create_engine
from sqlalchemy.dialects import registry  # type: ignore
from sqlalchemy.engine import Engine
from sqlalchemy.engine.base import Connection
from sqlalchemy.orm import Session, sessionmaker
from typing_extensions import ParamSpec

warnings.filterwarnings(
    "ignore",
    "distutils Version classes are deprecated. Use packaging.version instead.",
    DeprecationWarning,
)
P = ParamSpec("P")

FuncT = TypeVar("FuncT", bound=Callable[..., Any])


def pytest_sessionstart(session: Any) -> None:
    tox_env_name = os.environ.get("TOX_ENV_NAME")
    if not tox_env_name or "-" not in tox_env_name:
        return

    duckdb_version = ".".join(tox_env_name.split("-")[1][len("duckdb") :])

    logging.info(f"Installing DuckDB version {duckdb_version} for testing")

    check_call([sys.executable, "-m", "pip", "install", f"duckdb=={duckdb_version}"])


pytest_sessionstart(None)


@fixture
def engine() -> Engine:
    registry.register("duckdb", "duckdb_engine", "Dialect")

    return create_engine("duckdb:///:memory:")


@fixture
def conn(engine: Engine) -> Generator[Connection, None, None]:
    with engine.connect() as conn:
        yield conn


@fixture
def session(engine: Engine) -> Session:
    return sessionmaker(bind=engine)()


def raises_msg(msg: str) -> Callable[[Callable[P, None]], Callable[P, None]]:
    def decorator(func: Callable[P, None]) -> Callable[P, None]:
        @wraps(func)
        def wrapped_test(*args: P.args, **kwargs: P.kwargs) -> None:
            with raises(RuntimeError, match=msg):
                func(*args, **kwargs)

        return wrapped_test

    return decorator
