"""
See https://duckdb.org/docs/sql/data_types/numeric for more information

Also
```sql
select * from duckdb_types where type_category = 'NUMERIC';
```
"""

from typing import Any

from sqlalchemy.dialects.postgresql.base import PGTypeCompiler
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import BigInteger, Integer, SmallInteger

# INTEGER	INT4, INT, SIGNED	-2147483648	2147483647
# SMALLINT	INT2, SHORT	-32768	32767
# BIGINT	INT8, LONG	-9223372036854775808	9223372036854775807
(BigInteger, SmallInteger)  # pure reexport


class UInt64(Integer):
    pass


class UInt32(Integer):
    pass


class UInt16(Integer):
    "AKA USMALLINT"


class UInt8(Integer):
    pass


class UTinyInteger(Integer):
    "AKA UInt1"
    name = "UTinyInt"
    # UTINYINT	-	0	255


class TinyInteger(Integer):
    "AKA Int1"
    name = "TinyInt"
    # TINYINT	INT1	-128	127


class USmallInteger(Integer):
    name = "usmallint"
    "AKA UInt2"
    # USMALLINT	-	0	65535
    min = 0
    max = 2**15


class UBigInteger(Integer):
    name = "UBigInt"
    min = 0
    max = 18446744073709551615


class HugeInteger(Integer):
    name = "HugeInt"
    # HUGEINT	 	-170141183460469231731687303715884105727*	170141183460469231731687303715884105727


class UInteger(Integer):
    # UINTEGER	-	0	4294967295
    pass


def compile_uint(element: Integer, compiler: PGTypeCompiler, **kw: Any) -> str:
    return getattr(element, "name", type(element).__name__)


types = [
    subclass
    for subclass in Integer.__subclasses__()
    if subclass.__module__ == UInt64.__module__
]
assert types


def register_extension_types() -> None:
    for subclass in types:
        compiles(subclass, "duckdb")(compile_uint)
