from sqlalchemy.testing import suite

suite = dict(suite.__dict__)
suite.pop("__file__")
suite.pop("ComponentReflectionTest")
suite.pop("SequenceTest")
suite.pop("HasSequenceTest")
suite.pop("HasIndexTest")
locals().update(suite)
