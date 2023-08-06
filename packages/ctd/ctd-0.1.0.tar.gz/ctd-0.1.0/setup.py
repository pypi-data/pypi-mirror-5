#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

from ctd import __version__ as version

url = 'http://pypi.python.org/packages/source'
install_requires = ['numpy', 'scipy', 'matplotlib', 'pandas', 'gsw']

classifiers = """\
Development Status :: 2 - Pre-Alpha
Environment :: Console
Intended Audience :: Science/Research
Intended Audience :: Developers
Intended Audience :: Education
License :: OSI Approved :: MIT License
Operating System :: OS Independent
Programming Language :: Python
Topic :: Scientific/Engineering
Topic :: Education
Topic :: Software Development :: Libraries :: Python Modules
"""

README = open('README.txt').read()
CHANGES = open('CHANGES.txt').read()
LICENSE = open('LICENSE.txt').read()

config = dict(name='ctd',
              version=version,
              packages=['ctd'],
              test_suite='test',
              use_2to3=True,
              license=LICENSE,
              long_description='%s\n\n%s' % (README, CHANGES),
              classifiers=filter(None, classifiers.split("\n")),
              description='Tools to load hydrographic data as DataFrames',
              author='Filipe Fernandes',
              author_email='ocefpaf@gmail.com',
              maintainer='Filipe Fernandes',
              maintainer_email='ocefpaf@gmail.com',
              url='http://pypi.python.org/pypi/ctd/',
              download_url='%s/c/ctd/ctd-%s.tar.gz' % (url, version),
              platforms='any',
              keywords=['oceanography', 'data analysis', 'cnv', 'DataFrame'],
              install_requires=install_requires)

setup(**config)
