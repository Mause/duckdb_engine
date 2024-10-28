from sqlalchemy import MetaData, create_engine, text

engine = create_engine("duckdb:///:memory:")
metadata = MetaData()
with engine.connect() as conn:
    conn.execute(text("CREATE TABLE tbl(col1 INTEGER)"))
    conn.commit()
try:
    metadata.reflect(engine)
except Exception as e:
    print("Exception: " + str(e))
    raise AssertionError