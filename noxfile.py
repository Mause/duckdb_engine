import re
from contextlib import contextmanager
from itertools import product
from typing import Generator, List

import github_action_utils as gha
import nox


@contextmanager
def group(title: str) -> Generator[None, None, None]:
    try:
        gha.start_group(title)
        yield
    finally:
        gha.end_group()


def expandvars(string: str) -> List[str]:
    bits = [
        part[1:-1].split(",") if part.startswith("{") else [part]
        for part in (re.split(r"(\{[^}]+})", string))
    ]
    return ["".join(s) for s in product(*bits)]


envlist = expandvars(
    "{mypy,duckdb040,duckdb051,duckdb061,duckdb071,duckdb081}-sqlalchemy{13,14,20}"
)


@nox.session(py=["3.7", "3.8", "3.9", "3.10", "3.11", "3.12"])
@nox.parametrize(
    "duckdb", ["0.5.1", "0.6.1", "0.7.1", "0.8.1", "0.9.1", "0.10.1", "master"]
)
@nox.parametrize("sqlalchemy", ["1.3", "1.4", "2.0"])
def tests(session: nox.Session, duckdb: str, sqlalchemy: str) -> None:
    with group(f"{session.name} - Install"):
        poetry(session)
        session.install(f"sqlalchemy~={sqlalchemy}")
        if duckdb == "master":
            session.install("duckdb", "--pre", "-U")
        else:
            session.install(f"duckdb=={duckdb}")
    with group(f"{session.name} Test"):
        session.run(
            "pytest",
            "--junitxml=results.xml",
            "--cov",
            "--cov-report",
            "xml:coverage.xml",
            "--verbose",
            "-rs",
            "--remote-data",
        )


def poetry(session: nox.Session) -> None:
    session.install("poetry")
    session.run("poetry", "install", "--with", "dev")


@nox.session()
def mypy(session: nox.Session) -> None:
    session.run("mypy", ".")


# passenv = HOME
# setenv =
#     SQLALCHEMY_WARN_20: true
# envlogdir = logs
