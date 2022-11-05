from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    MetaData,
    Sequence,
    String,
    Table,
    create_engine,
)
from sqlalchemy.engine import Engine
from sqlalchemy_schemadisplay import create_schema_graph


def display_schema(engine: Engine, outfile: str) -> None:
    """
    Display metadata
    """
    m = MetaData(engine)
    # create the pydot graph object by autoloading all tables via a bound metadata object
    graph = create_schema_graph(
        metadata=m,
        show_datatypes=False,  # The image would get nasty big if we'd show the datatypes
        show_indexes=False,  # ditto for indexes
        rankdir="LR",  # From left to right (instead of top to bottom)
        concentrate=False,  # Don't try to join the relation lines together
    )
    graph.write_png(outfile)  # write out the file


def test_graph() -> None:
    # Second test with duckdb
    engine = create_engine("duckdb:///:memory:")

    metadata_obj = MetaData(engine)

    user_id_seq: Sequence = Sequence("user_id_seq")

    Table(
        "user",
        metadata_obj,
        Column(
            "user_id",
            Integer,
            user_id_seq,
            server_default=user_id_seq.next_value(),
            primary_key=True,
        ),
        Column("user_name", String(16), nullable=False),
        Column("email_address", String(60), key="email"),
        Column("nickname", String(50), nullable=False),
    )

    user_prefs_id_seq: Sequence = Sequence("user_prefs_id_seq")

    Table(
        "user_prefs",
        metadata_obj,
        Column(
            "pref_id",
            Integer,
            user_prefs_id_seq,
            server_default=user_prefs_id_seq.next_value(),
            primary_key=True,
        ),
        Column("user_id", Integer, ForeignKey("user.user_id"), nullable=False),
        Column("pref_name", String(40), nullable=False),
        Column("pref_value", String(100)),
    )

    metadata_obj.create_all(engine)

    display_schema(engine, "duckdb/dbschema_2.png")
