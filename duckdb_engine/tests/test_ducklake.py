import tempfile
from pathlib import Path
from typing import Generator

import pytest
from sqlalchemy.dialects import registry  # type: ignore
from sqlalchemy import create_engine, inspect, text
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
    engine = create_engine(f"duckdb:///ducklake:{catalog_path}", 
                           connect_args={"data_path": str(data_path), "alias": "test_ducklake" }
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


def test_ducklake_query_table(ducklake_engine: Engine, temp_dir: Path):

    
    with ducklake_engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE test_table (
                id INTEGER, 
                name VARCHAR, 
                value DOUBLE
            )
        """))
        
        conn.execute(text("""
            INSERT INTO test_table VALUES 
            (1, 'Alice', 100.5),
            (2, 'Bob', 200.7),
            (3, 'Charlie', 300.9)
        """))
        
        result = conn.execute(text("SELECT COUNT(*) FROM test_table"))
        assert result.scalar() == 3
        
        result = conn.execute(text("SELECT name FROM test_table WHERE id = 2"))
        assert result.scalar() == "Bob"
        
        result = conn.execute(text("SELECT AVG(value) FROM test_table"))
        avg_value = result.scalar()
        assert abs(avg_value - 200.7) < 0.01


def test_ducklake_query_schema(ducklake_engine: Engine, temp_dir: Path):
    with ducklake_engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA test_schema"))
        
        conn.execute(text("""
            CREATE TABLE test_schema.schema_table (
                id INTEGER, 
                description VARCHAR
            )
        """))
        
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


def test_ducklake_query_view(ducklake_engine: Engine, temp_dir: Path):
    
    with ducklake_engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA test_schema"))
        conn.execute(text("use test_schema"))

        
        conn.execute(text("""
            CREATE TABLE test_schema.base_table (
                id INTEGER, 
                category VARCHAR, 
                amount DOUBLE
            )
        """))
        
        conn.execute(text("""
            INSERT INTO test_schema.base_table VALUES 
            (1, 'A', 100.0),
            (2, 'B', 200.0),
            (3, 'A', 150.0),
            (4, 'B', 250.0)
        """))
        
        conn.execute(text("""
            CREATE VIEW category_summary AS 
            SELECT category, SUM(amount) as total_amount, COUNT(*) as count 
            FROM test_ducklake.test_schema.base_table 
            GROUP BY category
        """))
        
        result = conn.execute(text("SELECT COUNT(*) FROM test_schema.category_summary"))
        assert result.scalar() == 2
        
        result = conn.execute(text("""
            SELECT total_amount FROM test_schema.category_summary WHERE category = 'A'
        """))
        assert result.scalar() == 250.0
        
        inspector = inspect(ducklake_engine)
        view_names = inspector.get_view_names('test_schema')
        assert "category_summary" in view_names