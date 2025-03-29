from sqlalchemy import Column, Integer, Sequence, String, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

Base = declarative_base()


class IcebergTables(Base):
    __tablename__ = "iceberg_tables"
    id = Column(Integer, Sequence("idseq"), primary_key=True)
    name = Column(String, nullable=False)


def test_lock(engine: Session) -> None:
    stmt = select(IcebergTables).with_for_update(of=IcebergTables)

    assert "FOR UPDATE" not in str(stmt.compile(engine))
