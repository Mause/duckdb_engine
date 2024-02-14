import os

from importlib_metadata import version
from pytest import mark

tox_env_name = os.environ.get("TOX_ENV_NAME")


@mark.skipif(not tox_env_name, reason="not running inside tox")
def test_versions() -> None:
    assert tox_env_name
    parts = version("duckdb").replace(".", "")

    if tox_env_name == "duckdb_master" or "mypy" in tox_env_name:
        return

    requested_version = tox_env_name.split("-")[1]
    installed_version = f"duckdb{parts}"

    assert requested_version == installed_version
