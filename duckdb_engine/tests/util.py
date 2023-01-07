import sqlalchemy
from packaging.version import Version
from pytest import mark

sqlalchemy_1_only = mark.skipif(
    Version(sqlalchemy.__version__).major > 1,
    reason="Pandas doesn't yet support sqlalchemy 2",
)
