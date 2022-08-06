# duckdb_engine

[![Supported Python Versions](https://img.shields.io/pypi/pyversions/duckdb-engine)](https://pypi.org/project/duckdb-engine/) [![PyPI version](https://badge.fury.io/py/duckdb-engine.svg)](https://badge.fury.io/py/duckdb-engine) [![codecov](https://codecov.io/gh/Mause/duckdb_engine/branch/master/graph/badge.svg)](https://codecov.io/gh/Mause/duckdb_engine)

Basic SQLAlchemy driver for [DuckDB](https://duckdb.org/)

## Installation
```sh
$ pip install duckdb-engine
```

DuckDB Engine also has a conda feedstock available, the instructions for the use of which are available in it's [repository](https://github.com/conda-forge/duckdb-engine-feedstock).

## Usage

Once you've installed this package, you should be able to just use it, as SQLAlchemy does a python path search

```python
from sqlalchemy import Column, Integer, Sequence, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session

Base = declarative_base()


class FakeModel(Base):  # type: ignore
    __tablename__ = "fake"

    id = Column(Integer, Sequence("fakemodel_id_sequence"), primary_key=True)
    name = Column(String)


eng = create_engine("duckdb:///:memory:")
Base.metadata.create_all(eng)
session = Session(bind=eng)

session.add(FakeModel(name="Frank"))
session.commit()

frank = session.query(FakeModel).one()

assert frank.name == "Frank"
```

## Configuration

You can configure DuckDB by passing `connect_args` to the create_engine function
```python
create_engine(
    'duckdb:///:memory:',
    connect_args={
        'read_only': True,
        'config': {
            'memory_limit': '500mb'
        }
    }
)
```

The supported configuration parameters are listed in the [DuckDB docs](https://duckdb.org/docs/sql/configuration)

## How to register a pandas DataFrame

```python
eng = create_engine("duckdb:///:memory:")
eng.execute("register", ("dataframe_name", pd.DataFrame(...)))

eng.execute("select * from dataframe_name")
```

## Things to keep in mind
Duckdb's SQL parser is based on the PostgreSQL parser, but not all features in PostgreSQL are supported in duckdb. Because the `duckdb_engine` dialect is derived from the `postgresql` dialect, `SQLAlchemy` may try to use PostgreSQL-only features. Below are some caveats to look out for.

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
The `pandas.read_sql()` method can read tables from `duckdb_engine` into DataFrames, but the `sqlalchemy.engine.result.ResultProxy` trips up when `fetchmany()` is called. Therefore, for now `chunksize=None` (default) is necessary when reading duckdb tables into DataFrames. For example:

```python
>>> import pandas as pd
>>> import sqlalchemy
>>> engine = sqlalchemy.create_engine('duckdb:////path/to/duck.db')
>>> df = pd.read_sql('users', engine)                ### Works as expected
>>> df = pd.read_sql('users', engine, chunksize=25)  ### Throws an exception
```

## The name

Yes, I'm aware this package should be named `duckdb-driver` or something, I wasn't thinking when I named it and it's too hard to change the name now
