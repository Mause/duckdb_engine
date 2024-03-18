import os

from importlib_metadata import version
from pytest import mark

tox_env_name = os.environ.get("TOX_ENV_NAME")


@mark.skipif(not tox_env_name, reason="not running inside tox")
def test_versions() -> None:
    assert tox_env_name
    parts = version("duckdb").replace(".", "")

    installed_version = f"duckdb{parts}"

    if tox_env_name == "duckdb_master":
        assert "dev" in installed_version
    elif "mypy" in tox_env_name:
        return

    requested_version = tox_env_name.split("-")[1]

    assert requested_version == installed_version
