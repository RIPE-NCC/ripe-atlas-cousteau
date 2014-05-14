#!/usr/bin/env python

from setuptools import setup

from ripe.atlas.cousteau import __version__

tests_require = [
    'nose',
    'coverage',
    'mock',
    'jsonschema'
]

setup(
    name='ripe.atlas.cousteau',
    version=__version__,
    packages=["ripe", "ripe.atlas", "ripe.atlas.cousteau"],
    namespace_packages=["ripe", "ripe.atlas"],
    include_package_data=True,
    description='Python wrapper for RIPE ATLAS API',
    author_email='atlas-dev@ripe.net',
    tests_require=tests_require,
    test_suite="nose.collector",
)
