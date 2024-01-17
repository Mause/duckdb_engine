# snapshottest: v1 - https://goo.gl/zC4yUc

from snapshottest import GenericRepr, Snapshot

snapshots = Snapshot()

snapshots["test_reflection 1"] = [
    GenericRepr(
        "({'idNum': 0, 'sessionNum': 0, 'sessionName': 'Parquet2021-11-04', 'instanceName': 'ParquetTest', 'smName': 'ParquetTestEngine'}, {'creationTime': datetime.datetime(2021, 11, 5, 0, 34, 49, 937000, tzinfo=<DstTzInfo 'Australia/Perth' AWST+8:00:00 STD>), 'updateTime': datetime.datetime(2021, 11, 5, 0, 34, 49, 937000, tzinfo=<DstTzInfo 'Australia/Perth' AWST+8:00:00 STD>), 'version': 0, 'deleted': False, 'completed': False}, 'style', 41, 'desc')"
    )
]
