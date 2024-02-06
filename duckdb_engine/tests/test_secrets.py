from typing import Any, Optional, Set

from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import text
from sqlalchemy.sql.ddl import SchemaGenerator

from duckdb_engine.secrets import Secret

Base = declarative_base()


class SecretDTO:
    __visit_name__ = "secret"

    def __init__(self, secret: Secret) -> None:
        self.name = secret.name
        self.secret = secret
        self.schema = None
        self.foreign_key_constraints = set()

    schema: Optional[str]
    foreign_key_constraints: Optional[Set[str]]
    _extra_dependencies = ""

    def __gt__(self, other: Secret) -> bool:
        return self.name > other.name

    def __hash__(self) -> int:
        return hash((type(self), self.secret))


class DuckDBSchemaGenerator(SchemaGenerator):
    def visit_secret(self, secret_dto: SecretDTO, **kw: Any) -> None:
        txt = secret_dto.secret.to_sql(self.dialect)

        self.connection.execute(text(txt))


def test_secrets(engine: Engine) -> None:
    add_table = getattr(Base.metadata, "_add_table")
    add_table(
        "SecretDTO",
        None,
        SecretDTO(Secret(name="name", secret_type="s3", provider="config")),
    )
    getattr(engine, "_run_ddl_visitor")(DuckDBSchemaGenerator, Base.metadata)
