# snapshottest: v1 - https://goo.gl/zC4yUc

from snapshottest import GenericRepr, Snapshot

snapshots = Snapshot()

snapshots[
    "test_parquet_with_declarative_base 1"
] = """SELECT simple."itemType", simple."stateId", simple."stateMeta", simple.style, simple.description
FROM "/home/me/duckdb_engine/duckdb_engine/tests/simple.parquet" AS simple"""

snapshots["test_parquet_with_declarative_base 2"] = [
    GenericRepr(
        "(41, {'idNum': 0, 'sessionNum': 0, 'sessionName': 'Parquet2021-11-04', 'instanceName': 'ParquetTest', 'smName': 'ParquetTestEngine'}, {'creationTime': datetime.datetime(2021, 11, 5, 0, 34, 49, 937000, tzinfo=<DstTzInfo 'Australia/Perth' AWST+8:00:00 STD>), 'updateTime': datetime.datetime(2021, 11, 5, 0, 34, 49, 937000, tzinfo=<DstTzInfo 'Australia/Perth' AWST+8:00:00 STD>), 'version': 0, 'deleted': False, 'completed': False}, 'style', 'desc')"
    )
]

snapshots["test_reflection 1"] = [
    GenericRepr(
        "({'idNum': 0, 'sessionNum': 0, 'sessionName': 'Parquet2021-11-04', 'instanceName': 'ParquetTest', 'smName': 'ParquetTestEngine'}, {'creationTime': datetime.datetime(2021, 11, 5, 0, 34, 49, 937000, tzinfo=<DstTzInfo 'Australia/Perth' AWST+8:00:00 STD>), 'updateTime': datetime.datetime(2021, 11, 5, 0, 34, 49, 937000, tzinfo=<DstTzInfo 'Australia/Perth' AWST+8:00:00 STD>), 'version': 0, 'deleted': False, 'completed': False}, 'style', 41, 'desc')"
    )
]
