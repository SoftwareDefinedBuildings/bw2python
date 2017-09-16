#!/usr/bin/env python

from setuptools import setup

setup(
    name="bw2python",
    version="0.6.1",
    description="Python bindings for Bosswave 2",
    author="Jack Kolb",
    author_email="jkolb@berkeley.edu",
    url="https://github.com/SoftwareDefinedBuildings/bw2python",
    packages=["bw2python"],
    package_dir={'bw2python': 'src'},
    install_requires = ['msgpack-python']
)
