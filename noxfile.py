from contextlib import contextmanager
from typing import Generator

import nox

nox.options.default_venv_backend = "uv"
nox.options.error_on_external_run = True


@contextmanager
def group(title: str) -> Generator[None, None, None]:
    try:
        import github_action_utils as gha
    except ImportError:
        # If github_action_utils is not available, just yield without starting a group
        # This allows the code to run outside of GitHub Actions
        yield
        return
    try:
        gha.start_group(title)
        yield
    except Exception as e:
        gha.end_group()
        gha.error(f"{title} failed with {e}")
        raise
    else:
        gha.end_group()


# TODO: "0.5.1", "0.6.1", "0.7.1", "0.8.1"
# TODO: 3.11, 3.12, 3.13
@nox.session(py=["3.9", "3.10"])
@nox.parametrize("duckdb", ["0.9.2", "1.0.0"])
@nox.parametrize("sqlalchemy", ["1.3", "1.4", "2.0.35"])
def tests(session: nox.Session, duckdb: str, sqlalchemy: str) -> None:
    tests_core(session, duckdb, sqlalchemy)


@nox.session(py=["3.9"])
def nightly(session: nox.Session) -> None:
    session.skip("DuckDB nightly installs are broken right now")
    tests_core(session, "master", "1.4")


def tests_core(session: nox.Session, duckdb: str, sqlalchemy: str) -> None:
    with group(f"{session.name} - Install"):
        uv_sync(session)
        operator = "==" if sqlalchemy.count(".") == 2 else "~="
        session.install(f"sqlalchemy{operator}{sqlalchemy}")
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
            env={
                "SQLALCHEMY_WARN_20": "true",
            },
        )


def uv_sync(session: nox.Session) -> None:
    session.run(
        "uv",
        "sync",
        "--verbose",
        "--active",
        silent=False,
        env={"UV_PROJECT_ENVIRONMENT": session.virtualenv.location},
    )


@nox.session(py=["3.9"])
def mypy(session: nox.Session) -> None:
    session.skip("We need to fix the mypy issues before running it")
    uv_sync(session)
    session.run("mypy", "duckdb_engine/")
