# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots["test_get_columns 1"] = [
    {
        "autoincrement": False,
        "comment": None,
        "default": None,
        "name": "id",
        "nullable": True,
        "type": GenericRepr("INTEGER()"),
    }
]

snapshots["test_get_schema_names 1"] = [
    'memory."hello world"',
    "memory.information_schema",
    "memory.main",
    '"my db"."cursed "" schema"',
    '"my db"."hello world"',
    '"my db".information_schema',
    '"my db".main',
    "system.information_schema",
    "system.main",
    "temp.information_schema",
    "temp.main",
]
