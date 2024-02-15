#!/usr/bin/env python3

import os
import sys
from subprocess import check_call


def main() -> None:
    install_duckdb()

    check_call(
        [
            sys.executable,
            "-m",
            "pytest",
            "--junitxml=results.xml",
            "--cov",
            "--cov-report",
            "xml:coverage.xml",
            "--verbose",
            "-rs",
            "--remote-data",
        ]
    )


def install_duckdb() -> None:
    tox_env_name = os.environ.get("TOX_ENV_NAME")
    if not tox_env_name or "-" not in tox_env_name:
        return

    duckdb_version = ".".join(tox_env_name.split("-")[1][len("duckdb") :])

    print(f"Installing DuckDB version {duckdb_version} for testing")

    check_call([sys.executable, "-m", "pip", "install", f"duckdb=={duckdb_version}"])


if __name__ == "__main__":
    main()
