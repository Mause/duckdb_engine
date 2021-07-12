from glob import glob
from os.path import expanduser

import nox

required_versions = ["3.6", "3.7", "3.8", "3.9", "3.10"]

pythons = glob(expanduser("~/.pyenv/*/versions/*/python.exe")) or required_versions
assert all(
    any(version in python for python in pythons) for version in required_versions
)

session = nox.session(
    python=pythons,
    reuse_venv=True,
)


@session
def tests(session):
    session.run("poetry", "install", external=True)
    session.run("pytest")


@session
def mypy(session):
    session.run("poetry", "install")
    session.run("mypy", ".")
