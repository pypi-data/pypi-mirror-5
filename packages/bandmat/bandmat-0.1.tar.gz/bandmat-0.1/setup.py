#!/usr/bin/python
"""A distutils-based script for distributing and installing bandmat."""

# Copyright 2013 Matt Shannon

# This file is part of bandmat.
# See `License` for details of license and warranty.

import os
from distutils.core import setup
from distutils.extension import Extension
from distutils.command.sdist import sdist

cython_locs = [
    ('bandmat', 'core_fast'),
]

with open('README.rst') as readmeFile:
    long_description = readmeFile.read()

# see "A note on setup.py" in README.rst for an explanation of the dev file
dev_mode = os.path.exists('dev')

if dev_mode:
    from Cython.Distutils import build_ext as cython_build_ext
    from Cython.Build import cythonize

    class cythonizing_sdist(sdist):
        """A cythonizing sdist command.

        This class is a custom sdist command which ensures all cython-generated
        C files are up-to-date before running the conventional sdist command.
        """
        def run(self):
            cythonize([ os.path.join(*loc)+'.pyx' for loc in cython_locs ])
            sdist.run(self)

    cmdclass = {'build_ext': cython_build_ext, 'sdist': cythonizing_sdist}
    ext_modules = [ Extension('.'.join(loc), [os.path.join(*loc)+'.pyx'])
                    for loc in cython_locs ]
else:
    cmdclass = {}
    ext_modules = [ Extension('.'.join(loc), [os.path.join(*loc)+'.c'])
                    for loc in cython_locs ]

setup(
    name = 'bandmat',
    version = '0.1',
    description = 'A banded matrix library for python.',
    url = 'http://github.com/MattShannon/bandmat',
    author = 'Matt Shannon',
    author_email = 'matt.shannon@cantab.net',
    license = '3-clause BSD (see License file)',
    packages = ['bandmat'],
    long_description = long_description,
    cmdclass = cmdclass,
    ext_modules = ext_modules,
)
