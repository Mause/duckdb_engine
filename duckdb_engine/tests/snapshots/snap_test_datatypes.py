# snapshottest: v1 - https://goo.gl/zC4yUc

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots[
    "test_interval 1"
] = """
CREATE TABLE test_table (
\tduration INTERVAL
)

"""
