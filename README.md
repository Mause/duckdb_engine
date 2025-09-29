# duckdb_engine

Native SQLAlchemy driver for [DuckDB](https://duckdb.org/)

## About This Fork

This is an fork of [Mause's original duckdb_engine](https://github.com/Mause/duckdb_engine). Many thanks to Mause for creating and continuing to maintain the original SQLAlchemy driver for DuckDB.

### Key Improvements in This Fork

- **Native DuckDB Inspector**: Replaced PostgreSQL-based inspector with a native DuckDB implementation for better compatibility and performance
- **Enhanced DuckDB Compatibility**: Improved support for DuckDB-specific features and native comment support
- **Unified Query Execution**: Cleaner, more maintainable inspector query execution system
- **Improved Sequence Support**: Better handling of sequences in schema introspection
- **Reduced Dependencies**: Removed reliance on PostgreSQL dialect for inspection operations

<!--ts-->
- [duckdb\_engine](#duckdb_engine)
  - [About This Fork](#about-this-fork)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Usage in IPython/Jupyter](#usage-in-ipythonjupyter)
  - [Configuration](#configuration)
  - [How to register a pandas DataFrame](#how-to-register-a-pandas-dataframe)
  - [Things to keep in mind](#things-to-keep-in-mind)
    - [Native DuckDB Inspector](#native-duckdb-inspector)
    - [General Compatibility Notes](#general-compatibility-notes)
    - [Auto-incrementing ID columns](#auto-incrementing-id-columns)
    - [Pandas `read_sql()` chunksize](#pandas-read_sql-chunksize)
    - [Unsigned integer support](#unsigned-integer-support)
  - [Alembic Integration](#alembic-integration)
  - [Preloading extensions (experimental)](#preloading-extensions-experimental)
  - [Registering Filesystems](#registering-filesystems)

## Installation

Since this is a fork and not the official PyPI package, install directly from GitHub:

```sh
# Install from GitHub
$ pip install git+https://github.com/gfrmin/duckdb_engine.git

# Or for development
$ git clone https://github.com/gfrmin/duckdb_engine.git
$ cd duckdb_engine
$ uv sync
```

**Note**: This fork is not available on PyPI or conda-forge. Use the GitHub installation method above.

### Development Setup

For development with this fork:

```sh
# Clone the repository
$ git clone https://github.com/gfrmin/duckdb_engine.git
$ cd duckdb_engine

# Install dependencies using uv
$ uv sync

# Run tests
$ uv run pytest

# Run with coverage
$ uv run pytest --cov

# Type checking
$ uv run mypy duckdb_engine/

# Formatting and linting
$ uv run ruff check --fix .
$ uv run ruff format .
```

## Usage

Once you've installed this package, you should be able to just use it, as SQLAlchemy does a python path search

```python
from sqlalchemy import Column, Integer, Sequence, String, create_engine
from sqlalchemy.orm import DeclarativeBase, Session

class Base(DeclarativeBase):
    pass

class FakeModel(Base):
    __tablename__ = "fake"

    id = Column(Integer, Sequence("fakemodel_id_sequence"), primary_key=True)
    name = Column(String)

eng = create_engine("duckdb:///:memory:")
Base.metadata.create_all(eng)

with Session(eng) as session:
    session.add(FakeModel(name="Frank"))
    session.commit()

    frank = session.query(FakeModel).one()
    assert frank.name == "Frank"
```

## Usage in IPython/Jupyter

With IPython-SQL and DuckDB-Engine you can query DuckDB natively in your notebook! Check out [DuckDB's documentation](https://duckdb.org/docs/guides/python/jupyter) or
Alex Monahan's great demo of this on [his blog](https://alex-monahan.github.io/2021/08/22/Python_and_SQL_Better_Together.html#an-example-workflow-with-duckdb).

## Configuration

You can configure DuckDB by passing `connect_args` to the create_engine function
```python
create_engine(
    'duckdb:///:memory:',
    connect_args={
        'read_only': False,
        'config': {
            'memory_limit': '500mb'
        }
    }
)
```

The supported configuration parameters are listed in the [DuckDB docs](https://duckdb.org/docs/sql/configuration)

## How to register a pandas DataFrame

```python
from sqlalchemy import create_engine, text
import pandas as pd

conn = create_engine("duckdb:///:memory:").connect()

# with SQLAlchemy 2.0+
conn.execute(text("register(:name, :df)"), {"name": "test_df", "df": pd.DataFrame(...)})

conn.execute(text("select * from test_df"))
```

**Requirements**: This fork requires Python 3.9+ and SQLAlchemy 2.0.43.

## Things to keep in mind

### Native DuckDB Inspector

This fork includes a **native DuckDB inspector** that provides better schema introspection than the original PostgreSQL-based approach. Key improvements include:

- **Better Type Mapping**: Native DuckDB type detection and mapping to SQLAlchemy types
- **Improved Performance**: Direct DuckDB system queries instead of PostgreSQL compatibility layer
- **Enhanced Sequence Support**: Native sequence introspection and management
- **Comment Support**: Full support for table and column comments
- **DuckDB-Specific Features**: Better support for DuckDB extensions and unique features

### General Compatibility Notes

While DuckDB's SQL parser is based on PostgreSQL, this fork reduces reliance on PostgreSQL-specific features through native DuckDB implementations. Below are some remaining considerations:

### Auto-incrementing ID columns
When defining an Integer column as a primary key, `SQLAlchemy` uses the `SERIAL` datatype for PostgreSQL. Duckdb does not yet support this datatype because it's a non-standard PostgreSQL legacy type, so a workaround is to use the `SQLAlchemy.Sequence()` object to auto-increment the key. For more information on sequences, you can find the [`SQLAlchemy Sequence` documentation here](https://docs.sqlalchemy.org/en/14/core/defaults.html#associating-a-sequence-as-the-server-side-default).

The following example demonstrates how to create an auto-incrementing ID column for a simple table:

```python
>>> import sqlalchemy
>>> engine = sqlalchemy.create_engine('duckdb:////path/to/duck.db')
>>> metadata = sqlalchemy.MetaData(engine)
>>> user_id_seq = sqlalchemy.Sequence('user_id_seq')
>>> users_table = sqlalchemy.Table(
...     'users',
...     metadata,
...     sqlalchemy.Column(
...         'id',
...         sqlalchemy.Integer,
...         user_id_seq,
...         server_default=user_id_seq.next_value(),
...         primary_key=True,
...     ),
... )
>>> metadata.create_all(bind=engine)
```

### Pandas `read_sql()` chunksize

**NOTE**: this is no longer an issue in versions `>=0.5.0` of `duckdb`

The `pandas.read_sql()` method can read tables from `duckdb_engine` into DataFrames, but the `sqlalchemy.engine.result.ResultProxy` trips up when `fetchmany()` is called. Therefore, for now `chunksize=None` (default) is necessary when reading duckdb tables into DataFrames. For example:

```python
>>> import pandas as pd
>>> import sqlalchemy
>>> engine = sqlalchemy.create_engine('duckdb:////path/to/duck.db')
>>> df = pd.read_sql('users', engine)                ### Works as expected
>>> df = pd.read_sql('users', engine, chunksize=25)  ### Throws an exception
```

### Unsigned integer support

Unsigned integers are supported by DuckDB, and are available in [`duckdb_engine.datatypes`](duckdb_engine/datatypes.py).

## Alembic Integration

SQLAlchemy's companion library `alembic` can optionally be used to manage database migrations.

This support can be enabling by adding an Alembic implementation class for the `duckdb` dialect.

```python
from alembic.ddl.impl import DefaultImpl

class AlembicDuckDBImpl(DefaultImpl):
    """Alembic implementation for DuckDB."""

    __dialect__ = "duckdb"
```

After loading this class with your program, Alembic will no longer raise an error when generating or applying migrations.

## Preloading extensions (experimental)

> DuckDB 0.9.0+ includes builtin support for autoinstalling and autoloading of extensions, see [the extension documentation](http://duckdb.org/docs/archive/0.9.0/extensions/overview#autoloadable-extensions) for more information.

Until the DuckDB python client allows you to natively preload extensions, I've added experimental support via a `connect_args` parameter

```python
from sqlalchemy import create_engine

create_engine(
    'duckdb:///:memory:',
    connect_args={
        'preload_extensions': ['https'],
        'config': {
            's3_region': 'ap-southeast-1'
        }
    }
)
```

## Registering Filesystems

> DuckDB allows registering filesystems from [fsspec](https://filesystem-spec.readthedocs.io/), see [documentation](https://duckdb.org/docs/guides/python/filesystems.html) for more information.

Support is provided under `connect_args` parameter

```python
from sqlalchemy import create_engine
from fsspec import filesystem

create_engine(
    'duckdb:///:memory:',
    connect_args={
        'register_filesystems': [filesystem('gcs')],
    }
)
```

