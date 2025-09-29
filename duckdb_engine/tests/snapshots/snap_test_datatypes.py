# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot

snapshots = Snapshot()

snapshots["test_enum 1"] = """
CREATE TYPE severity AS ENUM ( 'LOW', 'MEDIUM', 'HIGH' );


CREATE TABLE bugs(severity ENUM('LOW', 'MEDIUM', 'HIGH'), PRIMARY KEY(severity));




"""
