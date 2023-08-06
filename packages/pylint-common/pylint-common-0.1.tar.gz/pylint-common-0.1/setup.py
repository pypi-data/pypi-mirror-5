# -*- coding: UTF-8 -*-
from distutils.core import setup
from setuptools import find_packages
import time


_version = "0.1"
_packages = find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"])

_short_description = "pylint-common is a Pylint plugin to improve Pylint error analysis of the" \
                     "standard Python library"


setup( name='pylint-common',
       url='https://github.com/landscapeio/pylint-common',
       author='landscape.io',
       author_email='code@landscape.io',
       description=_short_description,
       version=_version,
       packages=_packages,
       install_requires=['pylint>=1.0', 'astroid>=1.0', 'pylint-plugin-utils>=0.1'],
       license='GPLv2',
       keywords='pylint stdlib plugin'
)
