from hypothesis import assume, given
from hypothesis.strategies import text
from pytest import fixture, mark
from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    MetaData,
    Sequence,
    String,
    Table,
    create_engine,
    inspect,
)
from sqlalchemy.dialects.postgresql.base import PGInspector
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import registry
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import RelationshipProperty, Session, relationship, sessionmaker


@fixture
def engine() -> Engine:
    registry.register("duckdb", "duckdb_engine", "Dialect")

    eng = create_engine("duckdb:///:memory:")
    Base.metadata.create_all(eng)
    return eng


Base = declarative_base()


class FakeModel(Base):  # type: ignore
    __tablename__ = "fake"

    id = Column(Integer, Sequence("fakemodel_id_sequence"), primary_key=True)
    name = Column(String)

    owner = relationship("Owner")  # type: RelationshipProperty[Owner]


class Owner(Base):  # type: ignore
    __tablename__ = "owner"
    id = Column(Integer, Sequence("owner_id"), primary_key=True)

    fake_id = Column(Integer, ForeignKey("fake.id"))
    owned = relationship(
        FakeModel, back_populates="owner"
    )  # type: RelationshipProperty[FakeModel]


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


def test_get_tables(engine: Engine) -> None:
    assert engine.table_names()


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


@mark.xfail(reason="reflection not yet supported in duckdb", raises=NotImplementedError)
def test_get_unique_constraints(inspector: PGInspector) -> None:
    inspector.get_unique_constraints("test", None)


def test_reflect(session: Session, engine: Engine) -> None:
    session.execute("create table test (id int);")
    session.commit()

    meta = MetaData(engine)
    meta.reflect(only=["test"])


def test_table_reflect(session: Session, engine: Engine) -> None:
    session.execute("create table test (id int);")
    session.commit()

    meta = MetaData()
    user_table = Table("test", meta)
    insp = inspect(engine)

    insp.reflect_table(user_table, None)


@mark.xfail(reason="current duckdb release doesnt support size param", raises=TypeError)
def test_fetch_df_chunks() -> None:
    import duckdb

    duckdb.connect(":memory:").execute("select 1").fetch_df_chunk(1)


@mark.xfail(
    reason="current duckdb release doesnt support size param", raises=RuntimeError
)
def test_description() -> None:
    import duckdb

    duckdb.connect("").description
