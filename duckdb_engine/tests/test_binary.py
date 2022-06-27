import sqlalchemy
from sqlalchemy import Column, Integer, select
from sqlalchemy.orm import Session, declarative_base
import sqlalchemy.types as types

from typing import Optional, Any

import zlib

Base = declarative_base()

id_seq = sqlalchemy.Sequence('id_seq')

def compress(s: str) -> bytes:
    return zlib.compress(s.encode("utf-8"), level=9)
def decompress(s: bytes) -> str:
    return zlib.decompress(s).decode("utf-8")

class CompressedString(types.TypeDecorator[str]):

    impl = types.BLOB

    def process_bind_param(self, value: Optional[str], dialect: Any) -> Optional[bytes]:
        if value is None:
            return None
        return compress(value)

    def process_result_value(self, value: bytes, dialect: Any) -> str:
        return decompress(value)

class A(Base):

    __tablename__ = "table_a"

    id = Column(Integer(), id_seq, server_default=id_seq.next_value(), primary_key=True)

    text = Column(CompressedString())

def test_binary():
    engine = sqlalchemy.create_engine("duckdb:///:memory:", echo=False, future=True)

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        a = A(text="Hello World!")
        session.add(a)
        session.commit()

    with Session(engine) as session:
        b: A = session.scalar(select(A))
        assert not (a is b)
        assert b.text == "Hello World!"

