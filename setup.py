#!/usr/bin/env python

from setuptools import setup

# import manually __version__ variable
exec(open('ripe/atlas/cousteau/version.py').read())

install_requires = ["python-dateutil", "socketIO-client>=0.6.5"]

tests_require = [
    "nose",
    "coverage",
    "mock",
    "jsonschema"
]

setup(
    name="ripe.atlas.cousteau",
    version=__version__,
    packages=["ripe", "ripe.atlas", "ripe.atlas.cousteau"],
    namespace_packages=["ripe", "ripe.atlas"],
    include_package_data=True,
    description="Python wrapper for RIPE ATLAS API",
    author_email="atlas-dev@ripe.net",
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="nose.collector",
)
