from dataclasses import dataclass
from typing import Optional

from sqlalchemy import String
from sqlalchemy.dialects.interfaces import Dialect
from sqlalchemy.orm import declarative_base

Base = declarative_base()


@dataclass(eq=True, frozen=True)
class Secret:
    """
    CREATE [OR REPLACE] [PERSISTENT | TEMPORARY] SECRET [IF NOT EXISTS] [secret_name] [IN storage_specifier] (
        TYPE secret_type,
        [PROVIDER provider,]
        [SCOPE path_or_list_of_paths,]
        [KEY1 value1],
        [KEY2 value2],
        ...
    );
    """

    name: str
    secret_type: str
    provider: str
    storage_specifier: Optional[str] = None
    scope: Optional[str] = None
    extra: Optional[dict] = None
    persist: bool = False

    def to_sql(self, dialect: Dialect) -> str:
        string_binder = String().literal_processor(dialect)

        prep = dialect.identifier_preparer.quote

        persist = "PERSISTENT" if self.persist else "TEMPORARY"
        txt = f"CREATE {persist} SECRET {prep(self.name)}"
        if self.storage_specifier:
            txt += f" IN {self.storage_specifier}"
        args = [
            f"TYPE {string_binder(self.secret_type)}",
            f"PROVIDER {string_binder(self.provider)}",
        ]
        if self.scope:
            args.append(f"SCOPE {self.scope}")
        for k, v in (self.extra or {}).items():
            args.append(f"{prep(k)} {string_binder(v)}")
        txt += f" ({', '.join(args)})"
        return txt
