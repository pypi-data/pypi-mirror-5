#! /usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
from os import path
from pkgutil import get_importer

# Calculate the base directory of the project to get relatives from.
BASE_DIR = path.abspath(path.dirname(__file__))

# Navigate, import, and retrieve the metadata of the project.
_imp = get_importer(path.join(BASE_DIR, 'src', 'vial'))
meta = _imp.find_module('meta').load_module('meta')

setup(
    name='vial',
    version=meta.version,
    description=meta.description,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.3'
    ],
    author='Concordus Applications',
    author_email='support@concordusapps.com',
    url='http://github.com/concordusapps/python-vial',
    package_dir={'vial': 'src/vial'},
    packages=find_packages(path.join(BASE_DIR, 'src')),
    install_requires=(
        # Python client for redis, an in-memory database that persists on disk.
        # <https://github.com/andymccurdy/redis-py>
        'redis',
    ),
    extras_require={
        'test': (
            # Test runner.
            'pytest',

            # Ensure PEP8 conformance.
            'pytest-pep8',

            # Ensure test coverage.
            'pytest-cov',
        )
    }
)
