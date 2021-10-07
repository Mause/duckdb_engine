from typing import TYPE_CHECKING, Any, Iterable, List, Tuple

import sqlparse
from sqlalchemy.engine import Connection
from sqlparse.engine import FilterStack
from sqlparse.engine.grouping import T_NAME, T_STRING
from sqlparse.sql import Identifier, Parenthesis
from sqlparse.tokens import Name, Token

if TYPE_CHECKING:
    from pandas import DataFrame


def pattern(token: Token, *pattern: type) -> List[Token]:
    assert len(token.tokens) == len(pattern)
    assert all(isinstance(tok, subp) for tok, subp in zip(token.tokens, pattern))
    return token.tokens


def prepare(statement: str, parameters: Tuple = None) -> Tuple[str, "DataFrame"]:
    stack = FilterStack()
    stack.enable_grouping()
    stack.preprocess.append(RemoveWhitespace())
    (statement,) = tuple(stack.run(statement))

    (func,) = pattern(statement, sqlparse.sql.Function)

    function_name, parens = pattern(func, Identifier, Parenthesis)

    assert function_name.tokens[0].match(sqlparse.tokens.Name, ("register",))

    assert parameters, "You must pass a dataframe as a parameter for this method"
    assert len(parameters) < 3, "Too many parameters"

    subs = parens._groupable_tokens[0]._groupable_tokens
    name, df = (token for token in subs if token.ttype in T_STRING + T_NAME)

    if name.ttype == Name.Placeholder:
        real_name = parameters[0]
        df = parameters[1]
        assert isinstance(real_name, str)
        return real_name, df
    else:
        return name.value, parameters[0]


def register_dataframe(
    con: Connection, statement: str, parameters: Tuple = None
) -> None:
    view_name, df = prepare(statement, parameters)
    view_name = view_name.strip("\"'")

    import pandas  # technically an optional dependency

    assert isinstance(df, pandas.DataFrame), df
    con.register(view_name, df)
    con.execute(
        "select 1"
    )  # dummy select so we can pretend the database was actually accessed


class RemoveWhitespace:
    def process(self, tokens: Iterable[Tuple[type, Any]]) -> Iterable[Tuple[type, Any]]:
        return (
            (ttype, token)
            for (ttype, token) in tokens
            if ttype != sqlparse.tokens.Whitespace
        )
