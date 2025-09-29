"""
See https://duckdb.org/docs/sql/data_types/numeric for more information

Also
```sql
select * from duckdb_types where type_category = 'NUMERIC';
```
"""

import typing
from typing import Any, Callable, Dict, Optional, Type

import duckdb
from packaging.version import Version
from sqlalchemy import exc
from sqlalchemy.engine import Dialect
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.sql import compiler, sqltypes, type_api
from sqlalchemy.sql.compiler import IdentifierPreparer
from sqlalchemy.sql.type_api import TypeEngine
from sqlalchemy.types import BigInteger, Integer, SmallInteger, String

# INTEGER	INT4, INT, SIGNED	-2147483648	2147483647
# SMALLINT	INT2, SHORT	-32768	32767
# BIGINT	INT8, LONG	-9223372036854775808	9223372036854775807
(BigInteger, SmallInteger)  # pure reexport

duckdb_version = duckdb.__version__

IS_GT_1 = Version(duckdb_version) > Version("1.0.0")


class UInt64(Integer):
    cache_ok = True


class UInt32(Integer):
    cache_ok = True


class UInt16(Integer):
    "AKA USMALLINT"

    cache_ok = True


class UInt8(Integer):
    cache_ok = True


class UTinyInteger(Integer):
    "AKA UInt1"

    cache_ok = True
    name = "UTinyInt"
    # UTINYINT	-	0	255


class TinyInteger(Integer):
    "AKA Int1"

    cache_ok = True
    name = "TinyInt"
    # TINYINT	INT1	-128	127


class USmallInteger(Integer):
    cache_ok = True
    name = "usmallint"
    "AKA UInt2"
    # USMALLINT	-	0	65535
    min = 0
    max = 2**15


class UBigInteger(Integer):
    cache_ok = True
    name = "UBigInt"
    min = 0
    max = 18446744073709551615


class HugeInteger(Integer):
    cache_ok = True
    name = "HugeInt"
    # HUGEINT	 	-170141183460469231731687303715884105727*	170141183460469231731687303715884105727


class UHugeInteger(Integer):
    cache_ok = True
    name = "UHugeInt"


class UInteger(Integer):
    # UINTEGER	-	0	4294967295
    cache_ok = True


if IS_GT_1:

    class VarInt(Integer):
        cache_ok = True


def compile_uint(
    element: Integer, compiler: compiler.GenericTypeCompiler, **kw: Any
) -> str:
    """Compile unsigned integer types for DuckDB"""
    return getattr(element, "name", type(element).__name__)


types = [
    subclass
    for subclass in Integer.__subclasses__()
    if subclass.__module__ == UInt64.__module__
]
assert types


TV = typing.Union[Type[TypeEngine], TypeEngine]


class Struct(TypeEngine):
    """
    Represents a STRUCT type in DuckDB

    ```python
    from duckdb_engine.datatypes import Struct
    from sqlalchemy import Table, Column, String

    Table(
        'hello',
        Column('name', Struct({'first': String, 'last': String})
    )
    ```

    :param fields: only optional due to limitations with how much type information DuckDB returns to us in the description field
    """

    __visit_name__ = "struct"
    cache_ok = True

    def __init__(self, fields: Optional[Dict[str, TV]] = None):
        self.fields = fields


class Map(TypeEngine):
    """
    Represents a MAP type in DuckDB

    ```python
    from duckdb_engine.datatypes import Map
    from sqlalchemy import Table, Column, String

    Table(
        'hello',
        Column('name', Map(String, String)
    )
    ```
    """

    __visit_name__ = "map"
    cache_ok = True
    key_type: TV
    value_type: TV

    def __init__(self, key_type: TV, value_type: TV):
        self.key_type = key_type
        self.value_type = value_type

    def bind_processor(
        self, dialect: Dialect
    ) -> Optional[Callable[[Optional[dict]], Optional[dict]]]:
        return lambda value: (
            {"key": list(value), "value": list(value.values())} if value else None
        )

    def result_processor(
        self, dialect: Dialect, coltype: str
    ) -> Optional[Callable[[Optional[dict]], Optional[dict]]]:
        if IS_GT_1:
            return lambda value: value
        else:
            return (
                lambda value: dict(zip(value["key"], value["value"])) if value else {}
            )


class Union(TypeEngine):
    """
    Represents a UNION type in DuckDB

    ```python
    from duckdb_engine.datatypes import Union
    from sqlalchemy import Table, Column, String

    Table(
        'hello',
        Column('name', Union({"name": String, "age": String})
    )
    ```
    """

    __visit_name__ = "union"
    cache_ok = True
    fields: Dict[str, TV]

    def __init__(self, fields: Dict[str, TV]):
        self.fields = fields


ISCHEMA_NAMES = {
    "hugeint": HugeInteger,
    "uhugeint": UHugeInteger,
    "tinyint": TinyInteger,
    "utinyint": UTinyInteger,
    "int8": BigInteger,
    "int4": Integer,
    "int2": SmallInteger,
    "timetz": sqltypes.TIME,
    "timestamptz": sqltypes.TIMESTAMP,
    "float4": sqltypes.FLOAT,
    "float8": sqltypes.FLOAT,
    "usmallint": USmallInteger,
    "uinteger": UInteger,
    "ubigint": UBigInteger,
    "timestamp_s": sqltypes.TIMESTAMP,
    "timestamp_ms": sqltypes.TIMESTAMP,
    "timestamp_ns": sqltypes.TIMESTAMP,
    "enum": sqltypes.Enum,
    "bool": sqltypes.BOOLEAN,
    "varchar": String,
    "text": sqltypes.TEXT,
    "json": sqltypes.JSON,
    "uuid": sqltypes.Uuid,
    "decimal": sqltypes.DECIMAL,
    "numeric": sqltypes.NUMERIC,
    "real": sqltypes.FLOAT,
    "double": sqltypes.FLOAT,
    "float": sqltypes.FLOAT,
    "date": sqltypes.DATE,
    "time": sqltypes.TIME,
    "timestamp": sqltypes.TIMESTAMP,
    "interval": sqltypes.Interval,
    "blob": sqltypes.LargeBinary,
    "bytea": sqltypes.LargeBinary,
    "struct": Struct,
    "map": Map,
    "union": Union,
}
if IS_GT_1:
    ISCHEMA_NAMES["varint"] = VarInt


def register_extension_types() -> None:
    for subclass in types:
        compiles(subclass, "duckdb")(compile_uint)


@compiles(Struct, "duckdb")  # type: ignore[misc]
def visit_struct(
    instance: Struct,
    compiler: compiler.GenericTypeCompiler,
    identifier_preparer: IdentifierPreparer,
    **kw: Any,
) -> str:
    """Compile STRUCT type for DuckDB"""
    return "STRUCT" + struct_or_union(instance, compiler, identifier_preparer, **kw)


@compiles(Union, "duckdb")  # type: ignore[misc]
def visit_union(
    instance: Union,
    compiler: compiler.GenericTypeCompiler,
    identifier_preparer: IdentifierPreparer,
    **kw: Any,
) -> str:
    """Compile UNION type for DuckDB"""
    return "UNION" + struct_or_union(instance, compiler, identifier_preparer, **kw)


def struct_or_union(
    instance: typing.Union[Union, Struct],
    compiler: compiler.GenericTypeCompiler,
    identifier_preparer: IdentifierPreparer,
    **kw: Any,
) -> str:
    """Generate the field specification for STRUCT or UNION types"""
    fields = instance.fields
    if fields is None:
        raise exc.CompileError(f"DuckDB {repr(instance)} type requires fields")
    return "({})".format(
        ", ".join(
            "{} {}".format(
                identifier_preparer.quote_identifier(key),
                process_type(
                    value, compiler, identifier_preparer=identifier_preparer, **kw
                ),
            )
            for key, value in fields.items()
        )
    )


def process_type(
    value: typing.Union[TypeEngine, Type[TypeEngine]],
    compiler: compiler.GenericTypeCompiler,
    **kw: Any,
) -> str:
    """Process a type through the compiler"""
    return compiler.process(type_api.to_instance(value), **kw)


@compiles(Map, "duckdb")  # type: ignore[misc]
def visit_map(instance: Map, compiler: compiler.GenericTypeCompiler, **kw: Any) -> str:
    """Compile MAP type for DuckDB"""
    return "MAP({}, {})".format(
        process_type(instance.key_type, compiler, **kw),
        process_type(instance.value_type, compiler, **kw),
    )
