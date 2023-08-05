#!/usr/bin/env python

from os.path import abspath, dirname, join
from setuptools import setup

# Fill in the long description (for the benefit of PyPi)
# with the contents of README.rst (rendered by GitHub).
readme_file = join(dirname(abspath(__file__)), 'README.rst')
readme_text = open(readme_file, 'r').read()

setup(name='verboselogs',
      version='1.0.1',
      description="Verbose logging for Python's logging module",
      long_description=readme_text,
      url='https://pypi.python.org/pypi/verboselogs',
      author='Peter Odding',
      author_email='peter@peterodding.com',
      py_modules=['verboselogs'])
