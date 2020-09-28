from pytest import fixture
from sqlalchemy import Column, Integer, Sequence, String, create_engine
from sqlalchemy.engine.url import registry
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


@fixture
def engine():
    registry.register("duckdb", "duckdb_engine", "Dialect")

    ewng = create_engine("duckdb:///:memory:")
    Base.metadata.create_all(ewng)
    return ewng


Base = declarative_base()


class FakeModel(Base):  # type: ignore
    __tablename__ = "fake"

    id = Column(Integer, Sequence("fakemodel_id_sequence"), primary_key=True)
    name = Column(String)


@fixture
def Session(engine):
    return sessionmaker(bind=engine)


@fixture
def session(Session):
    return Session()


def test_basic(session):
    session.add(FakeModel(name="Frank"))
    session.commit()

    frank = session.query(FakeModel).one()  # act

    assert frank.name == "Frank"
