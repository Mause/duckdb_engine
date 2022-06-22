from sqlalchemy.dialects import registry

registry.register("duckdb", "duckdb_engine", "Dialect")  # type: ignore
registry.register("duckdb.duckdb_engine", "duckdb_engine", "Dialect")  # type: ignore

pytest_plugins = "sqlalchemy.testing.plugin.pytestplugin"
