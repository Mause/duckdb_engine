from typing import TYPE_CHECKING, List
from uuid import uuid4

from pytest import importorskip
from sqlalchemy.dialects import registry  # type: ignore

importorskip("superset")


registry.register("duckdb", "duckdb_engine", "Dialect")

if TYPE_CHECKING:
    from superset.app import SupersetApp


def get_app() -> "SupersetApp":
    from flask_migrate import upgrade
    from superset.app import SupersetApp, SupersetAppInitializer
    from superset.initialization import appbuilder

    app = SupersetApp(__name__)
    app.config.from_object("superset.config")
    app.config["WTF_CSRF_METHODS"] = {}
    init = SupersetAppInitializer(app)
    init.pre_init()
    init.init_app()

    with app.app_context():
        upgrade()

        sm = appbuilder.sm
        role = sm.get_public_role()

        def add(view_menu: str, permissions: List[str]) -> None:
            sm.add_permissions_view(base_permissions=permissions, view_menu=view_menu)
            view_menu_db = sm.add_view_menu(view_menu)

            for view in sm.find_permissions_view_menu(view_menu_db):
                sm.add_permission_role(role, view)

        add("Database", ["can_write"])
        add("Superset", ["can_sql_json"])
        add("all_query_access", ["all_query_access"])
        add("all_database_access", ["all_database_access"])
        add("all_datasource_access", ["all_datasource_access"])

    return app


def test_superset(app: SupersetApp) -> None:
    from flask.testing import Client

    database_name = f"test-duckdb-{uuid4()}"

    client = Client(app)
    result = client.post(
        "/api/v1/database/",
        json={
            "database_name": database_name,
            "sqlalchemy_uri": "duckdb:///:memory:",
            "configuration_method": "dynamic_form",
            "parameters": {
                "engine": "duckdb",
                "connect_args": {
                    "preload_extensions": ["httpfs"],
                    "config": {
                        "s3_endpoint": "minio:9000",
                        "s3_access_key_id": "XXX",
                        "s3_secret_access_key": "XXX",
                        "s3_url_style": "path",
                        "s3_use_ssl": "False",
                    },
                },
            },
        },
    )
    assert result.status == "201 CREATED", (result.status, result.json)
    print(result.json)

    # sqllab
    result = client.post(
        "/superset/sql_json/",
        json={
            "database_id": result.json["id"],
            "sql": "select current_setting('s3_use_ssl')",
        },
    )
    assert result.status == "201 CREATED", (result.status, result.json)


if __name__ == "__main__":
    test_superset(get_app())
