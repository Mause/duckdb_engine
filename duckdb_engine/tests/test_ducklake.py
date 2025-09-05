import tempfile
from pathlib import Path
from typing import Generator

import pytest
import sqlalchemy
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.dialects import registry  # type: ignore
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def ducklake_engine(temp_dir: Path) -> Engine:
    data_path = temp_dir / "data"
    data_path.mkdir()
    registry.register("duckdb", "duckdb_engine", "Dialect")
    catalog_path = temp_dir / "test_catalog.ducklake"
    data_path = temp_dir / "data"
    engine = create_engine(
        f"duckdb:///ducklake:{catalog_path}",
        connect_args={"data_path": str(data_path), "alias": "test_ducklake"},
    )
    return engine


@pytest.fixture
def ducklake_session(ducklake_engine: Engine) -> Session:
    return sessionmaker(bind=ducklake_engine)()


def test_ducklake_attach_basic(ducklake_engine: Engine, temp_dir: Path):
    with ducklake_engine.connect() as conn:
        conn.execute(text("INSTALL ducklake"))
        conn.execute(text("LOAD ducklake"))

        result = conn.execute(text("SELECT current_database()"))
        assert result.scalar() is not None

        conn.execute(text("USE test_ducklake"))
        current_db = conn.execute(text("SELECT current_database()"))
        assert current_db.scalar() == "test_ducklake"


<<<<<<< HEAD
def test_ducklake_query_table(ducklake_engine: Engine)->None:


=======
def test_ducklake_query_table(ducklake_engine: Engine, temp_dir: Path):
>>>>>>> a9876c550c3070158618c3633b33d11a6fdc57e9
    with ducklake_engine.connect() as conn:
        conn.execute(
            text("""
            CREATE TABLE test_table (
                id INTEGER,
                name VARCHAR,
                value DOUBLE
            )
        """)
        )

        conn.execute(
            text("""
            INSERT INTO test_table VALUES
            (1, 'Alice', 100.5),
            (2, 'Bob', 200.7),
            (3, 'Charlie', 300.9)
        """)
        )

        result = conn.execute(text("SELECT COUNT(*) FROM test_table"))
        assert result.scalar() == 3

        result = conn.execute(text("SELECT name FROM test_table WHERE id = 2"))
        assert result.scalar() == "Bob"

        result = conn.execute(text("SELECT AVG(value) FROM test_table"))
        avg_value = result.scalar()
        assert abs(avg_value - 200.7) < 0.01


def test_ducklake_query_schema(ducklake_engine: Engine) -> None:
    with ducklake_engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA test_schema"))

        conn.execute(
            text("""
            CREATE TABLE test_schema.schema_table (
                id INTEGER,
                description VARCHAR
            )
        """)
        )

        inspector = inspect(ducklake_engine)
        schemas = inspector.get_schema_names()
        print(f"Schemas: {schemas}")
        assert "test_ducklake.test_schema" in schemas

        tables = inspector.get_table_names(schema="test_ducklake.test_schema")
        assert "schema_table" in tables

        columns = inspector.get_columns("schema_table", schema="test_schema")
        column_names = [col["name"] for col in columns]
        assert "id" in column_names
        assert "description" in column_names


<<<<<<< HEAD
def test_ducklake_query_view(ducklake_engine: Engine) -> None:

=======
def test_ducklake_query_view(ducklake_engine: Engine, temp_dir: Path):
>>>>>>> a9876c550c3070158618c3633b33d11a6fdc57e9
    with ducklake_engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA test_schema"))
        conn.execute(text("use test_schema"))

        conn.execute(
            text("""
            CREATE TABLE test_schema.base_table (
                id INTEGER,
                category VARCHAR,
                amount DOUBLE
            )
        """)
        )

        conn.execute(
            text("""
            INSERT INTO test_schema.base_table VALUES
            (1, 'A', 100.0),
            (2, 'B', 200.0),
            (3, 'A', 150.0),
            (4, 'B', 250.0)
        """)
        )

        conn.execute(
            text("""
            CREATE VIEW category_summary AS
            SELECT category, SUM(amount) as total_amount, COUNT(*) as count
            FROM test_ducklake.test_schema.base_table
            GROUP BY category
        """)
        )

        result = conn.execute(text("SELECT COUNT(*) FROM test_schema.category_summary"))
        assert result.scalar() == 2

        result = conn.execute(
            text("""
            SELECT total_amount FROM test_schema.category_summary WHERE category = 'A'
        """)
        )
        assert result.scalar() == 250.0

        inspector = inspect(ducklake_engine)
        view_names = inspector.get_view_names("test_schema")
        assert "category_summary" in view_names


@pytest.fixture
def readonly_ducklake_engine(temp_dir: Path) -> Engine:
    data_path = temp_dir / "data"
    data_path.mkdir()
    registry.register("duckdb", "duckdb_engine", "Dialect")
    catalog_path = temp_dir / "test_catalog.ducklake"

    # First create some test data with a writable connection
    writable_engine = create_engine(
        f"duckdb:///ducklake:{catalog_path}",
        connect_args={"data_path": str(data_path), "alias": "test_readonly"},
    )
    with writable_engine.connect() as conn:
        conn.execute(
            text("""
            CREATE TABLE readonly_test (
                id INTEGER,
                name VARCHAR
            )
        """)
        )
        conn.execute(text("INSERT INTO readonly_test VALUES (1, 'existing_data')"))

    # Return readonly engine
    readonly_engine = create_engine(
        f"duckdb:///ducklake:{catalog_path}",
        connect_args={
            "data_path": str(data_path),
            "alias": "test_readonly",
            "read_only": True,
        },
    )
    return readonly_engine


def test_ducklake_readonly_prevents_writes(readonly_ducklake_engine: Engine)-> None:
    with readonly_ducklake_engine.connect() as conn:
        # Read operations should work
        result = conn.execute(text("SELECT COUNT(*) FROM readonly_test"))
        assert result.scalar() == 1

        result = conn.execute(text("SELECT name FROM readonly_test WHERE id = 1"))
        assert result.scalar() == "existing_data"

        # Write operations should fail
        # sqlalchemy.exc.ProgrammingError: (duckdb.duckdb.InvalidInputException) Invalid Input Error: Cannot execute statement of type "INSERT" on database "test_readonly" which is attached in read-only mode!
        with pytest.raises(sqlalchemy.exc.ProgrammingError):
            conn.execute(text("INSERT INTO readonly_test VALUES (2, 'new_data')"))

        with pytest.raises(sqlalchemy.exc.ProgrammingError):
            conn.execute(text("DELETE FROM readonly_test WHERE id = 1"))

        with pytest.raises(sqlalchemy.exc.ProgrammingError):
            conn.execute(text("UPDATE readonly_test SET name = 'updated' WHERE id = 1"))

        with pytest.raises(sqlalchemy.exc.ProgrammingError):
            conn.execute(text("CREATE TABLE new_table (id INTEGER)"))

        with pytest.raises(sqlalchemy.exc.ProgrammingError):
            conn.execute(text("DROP TABLE readonly_test"))
