from functools import wraps
from typing import Any, Callable, TypeVar

from pytest import fixture, raises
from sqlalchemy import create_engine
from sqlalchemy.dialects import registry  # type: ignore
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from typing_extensions import ParamSpec

P = ParamSpec("P")

FuncT = TypeVar("FuncT", bound=Callable[..., Any])


@fixture()
def engine() -> Engine:
    registry.register("duckdb", "duckdb_engine", "Dialect")

    return create_engine("duckdb:///:memory:")


@fixture()
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
