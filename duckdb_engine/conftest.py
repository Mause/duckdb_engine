import os
import warnings

warnings.simplefilter("error")

assert 'SQLALCHEMY_WARN_20' in os.environ
