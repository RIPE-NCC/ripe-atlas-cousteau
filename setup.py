#!/usr/bin/env python
from os.path import abspath, dirname, join
from setuptools import setup

# import manually __version__ variable
exec(open('ripe/atlas/cousteau/version.py').read())

install_requires = [
    "python-dateutil", "socketIO-client>=0.6.5", "requests>=2.7.0"]

tests_require = [
    "pbr<=1.6",
    "nose",
    "coverage",
    "mock",
    "jsonschema"
]


# Get proper long description for package
current_dir = dirname(abspath(__file__))
description = open(join(current_dir, "README.rst")).read()
changes = open(join(current_dir, "CHANGES.rst")).read()
long_description = '\n\n'.join([description, changes])

setup(
    name="ripe.atlas.cousteau",
    version=__version__,
    packages=["ripe", "ripe.atlas", "ripe.atlas.cousteau"],
    namespace_packages=["ripe", "ripe.atlas"],
    include_package_data=True,
    license="GPLv3",
    url="https://github.com/RIPE-NCC/ripe-atlas-cousteau",
    description="Python wrapper for RIPE Atlas API",
    long_description=long_description,
    author="RIPE Atlas Development Team",
    author_email="atlas-dev@ripe.net",
    maintainer="Andreas Strikos",
    maintainer_email="astrikos@ripe.net",
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite="nose.collector",
    keywords=['RIPE', 'RIPE NCC', 'RIPE Atlas'],
    classifiers=[
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Topic :: Internet :: WWW/HTTP"
    ]
)
