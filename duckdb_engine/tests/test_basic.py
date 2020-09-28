from pytest import fixture
from sqlalchemy import Column, ForeignKey, Integer, Sequence, String, create_engine
from sqlalchemy.engine.url import registry
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


@fixture
def engine():
    registry.register("duckdb", "duckdb_engine", "Dialect")

    eng = create_engine("duckdb:///:memory:")
    Base.metadata.create_all(eng)
    return eng


Base = declarative_base()


class FakeModel(Base):  # type: ignore
    __tablename__ = "fake"

    id = Column(Integer, Sequence("fakemodel_id_sequence"), primary_key=True)
    name = Column(String)

    owner = relationship("Owner")


class Owner(Base):  # type: ignore
    __tablename__ = "owner"
    id = Column(Integer, Sequence("owner_id"), primary_key=True)

    fake_id = Column(Integer, ForeignKey("fake.id"))
    owned = relationship("FakeModel", back_populates="owner")


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


def test_foreign(session):
    model = FakeModel(name="Walter")
    session.add(model)
    session.add(Owner(owned=model))
    session.commit()

    owner = session.query(Owner).one()  # act

    assert owner.owned.name == "Walter"
