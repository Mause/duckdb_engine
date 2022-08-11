from sqlalchemy.engine import Engine
from sqlalchemy.testing.provision import temp_table_keyword_args
from sqlalchemy.testing.requirements import SuiteRequirements, exclusions


class Requirements(SuiteRequirements):
    @property
    def schemas(self) -> exclusions.Compound:
        return exclusions.closed()


@temp_table_keyword_args.for_db("duckdb")  # type: ignore
def spanner_temp_table_keyword_args(cfg: dict, eng: Engine) -> dict:
    return {}
