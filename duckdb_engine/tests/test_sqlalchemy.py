from sqlalchemy.testing import suite

suite = dict(suite.__dict__)
suite.pop("__file__")
locals().update(suite)
