#!/usr/bin/env python

from setuptools import setup, find_packages

from ripeatlas import __version__


setup(
    name='ripeatlas',
    version=__version__,
    description='Python wrapper for RIPE ATLAS API',
    author_email='atlas-dev@ripe.net',
    packages=find_packages(),
)
