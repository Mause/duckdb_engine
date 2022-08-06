import zlib
from datetime import timedelta
from pathlib import Path
from typing import Any, Optional

import duckdb
from hypothesis import assume, given, settings
from hypothesis.strategies import text
from pytest import fixture, importorskip, mark, raises
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    Interval,
    MetaData,
    Sequence,
    String,
    Table,
    create_engine,
    inspect,
    select,
    types,
)
from sqlalchemy.dialects import registry
from sqlalchemy.dialects.postgresql.base import PGInspector
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import RelationshipProperty, Session, relationship, sessionmaker

from .. import DBAPI


@fixture
def engine() -> Engine:
    registry.register("duckdb", "duckdb_engine", "Dialect")  # type: ignore

    eng = create_engine("duckdb:///:memory:")
    Base.metadata.create_all(eng)
    return eng


Base = declarative_base()


class CompressedString(types.TypeDecorator):
    """Custom Column Type"""

    impl = types.BLOB

    def process_bind_param(self, value: Optional[str], dialect: Any) -> Optional[bytes]:  # type: ignore
        if value is None:
            return None
        return zlib.compress(value.encode("utf-8"), level=9)

    def process_result_value(self, value: bytes, dialect: Any) -> str:  # type: ignore
        return zlib.decompress(value).decode("utf-8")


class TableWithBinary(Base):

    __tablename__ = "table_with_binary"

    id = Column(Integer(), Sequence("id_seq"), primary_key=True)

    text = Column(CompressedString())


class FakeModel(Base):
    __tablename__ = "fake"

    id = Column(Integer, Sequence("fakemodel_id_sequence"), primary_key=True)
    name = Column(String)

    owner = relationship("Owner")  # type: RelationshipProperty[Owner]


class Owner(Base):
    __tablename__ = "owner"
    id = Column(Integer, Sequence("owner_id"), primary_key=True)

    fake_id = Column(Integer, ForeignKey("fake.id"))
    owned = relationship(
        FakeModel, back_populates="owner"
    )  # type: RelationshipProperty[FakeModel]


class IntervalModel(Base):
    __tablename__ = "IntervalModel"

    id = Column(Integer, Sequence("IntervalModel_id_sequence"), primary_key=True)

    field = Column(Interval)


@fixture
def session(engine: Engine) -> Session:
    return sessionmaker(bind=engine)()


def test_basic(session: Session) -> None:
    session.add(FakeModel(name="Frank"))
    session.commit()

    frank = session.query(FakeModel).one()  # act

    assert frank.name == "Frank"


def test_foreign(session: Session) -> None:
    model = FakeModel(name="Walter")
    session.add(model)
    session.add(Owner(owned=model))
    session.commit()

    owner = session.query(Owner).one()  # act

    assert owner.owned.name == "Walter"


@given(text())
@settings(deadline=timedelta(seconds=1))
def test_simple_string(s: str) -> None:
    assume("\x00" not in s)
    eng = create_engine("duckdb:///:memory:")
    Base.metadata.create_all(eng)
    session = sessionmaker(bind=eng)()
    model = FakeModel(name=s)
    session.add(model)
    session.add(Owner(owned=model))
    session.commit()

    owner = session.query(Owner).one()  # act

    assert owner.owned.name == s


def test_get_tables(inspector: PGInspector) -> None:
    assert inspector.get_table_names()
    assert inspector.get_view_names() == []


def test_get_views(engine: Engine) -> None:
    con = engine.connect()
    views = engine.dialect.get_view_names(con)
    assert views == []

    engine.execute("create view test as select 1")

    con = engine.connect()
    views = engine.dialect.get_view_names(con)
    assert views == ["test"]


@fixture
def inspector(engine: Engine, session: Session) -> PGInspector:
    session.execute("create table test (id int);")
    session.commit()

    meta = MetaData()
    Table("test", meta)

    return inspect(engine)


def test_get_columns(inspector: PGInspector) -> None:
    inspector.get_columns("test", None)


def test_get_foreign_keys(inspector: PGInspector) -> None:
    inspector.get_foreign_keys("test", None)


@mark.xfail(reason="reflection not yet supported in duckdb", raises=NotImplementedError)
def test_get_check_constraints(inspector: PGInspector) -> None:
    inspector.get_check_constraints("test", None)


def test_get_unique_constraints(inspector: PGInspector) -> None:
    inspector.get_unique_constraints("test", None)


def test_reflect(session: Session, engine: Engine) -> None:
    session.execute("create table test (id int);")
    session.commit()

    meta = MetaData(engine)
    meta.reflect(only=["test"])


def test_commit(session: Session, engine: Engine) -> None:
    session.execute("commit;")

    InteractiveShell = importorskip("IPython.core.interactiveshell").InteractiveShell

    shell = InteractiveShell()
    assert not shell.run_line_magic("load_ext", "sql")
    assert not shell.run_line_magic("sql", "duckdb:///:memory:")
    assert shell.run_line_magic("sql", "select 42;") == [(42,)]


def test_table_reflect(session: Session, engine: Engine) -> None:
    session.execute("create table test (id int);")
    session.commit()

    meta = MetaData()
    user_table = Table("test", meta)
    insp = inspect(engine)

    insp.reflect_table(user_table, None)


def test_fetch_df_chunks() -> None:
    import duckdb

    duckdb.connect(":memory:").execute("select 1").fetch_df_chunk(1)


def test_description() -> None:
    import duckdb

    duckdb.connect("").description


def test_intervals(session: Session) -> None:
    session.add(IntervalModel(field=timedelta(days=1)))
    session.commit()

    owner = session.query(IntervalModel).one()  # act

    assert owner.field == timedelta(days=1)


def test_binary(session: Session) -> None:

    a = TableWithBinary(text="Hello World!")
    session.add(a)
    session.commit()

    b: TableWithBinary = session.scalar(select(TableWithBinary))  # type: ignore
    assert b.text == "Hello World!"


def test_comment_support() -> None:
    "comments not yet supported by duckdb"
    exc = getattr(duckdb, "StandardException", DBAPI.Error)

    with raises(exc, match="syntax error"):
        duckdb.default_connection.execute('comment on sqlite_master is "hello world";')


@mark.xfail(raises=AttributeError)
def test_rowcount() -> None:
    import duckdb

    duckdb.default_connection.rowcount


def test_sessions(session: Session) -> None:
    c = IntervalModel(field=timedelta(seconds=5))
    session.add(c)
    session.commit()

    c = session.get(IntervalModel, 1)  # type: ignore
    c.field = timedelta(days=5)
    session.flush()
    session.commit()


def test_inmemory() -> None:
    InteractiveShell = importorskip("IPython.core.interactiveshell").InteractiveShell

    shell = InteractiveShell()
    shell.run_cell("""import sqlalchemy as sa""")
    shell.run_cell("""eng = sa.create_engine("duckdb:///:memory:")""")
    shell.run_cell("""eng.execute("CREATE TABLE t (x int)")""")
    res = shell.run_cell("""eng.execute("SHOW TABLES").fetchall()""")

    assert res.result == [("t",)]


def test_config(tmp_path: Path) -> None:
    db_path = tmp_path / "test.db"

    with duckdb.connect(str(db_path)) as db:
        db.execute("create table hello1 (i int)")

    eng = create_engine(
        f"duckdb:///{db_path}",
        connect_args={"read_only": True, "config": {"memory_limit": "500mb"}},
    )

    with raises(
        DBAPIError, match='Cannot execute statement of type "CREATE" in read-only mode!'
    ):
        eng.execute("create table hello2 (i int)")
