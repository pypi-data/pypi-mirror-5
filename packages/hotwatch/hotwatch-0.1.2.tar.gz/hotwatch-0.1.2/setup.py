#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

from distribute_setup import use_setuptools; use_setuptools()
from setuptools import setup


rel_file = lambda *args: os.path.join(os.path.dirname(os.path.abspath(__file__)), *args)

def read_from(filename):
    fp = open(filename)
    try:
        return fp.read()
    finally:
        fp.close()

def get_long_description():
    return read_from(rel_file('README.rst'))

def get_requirements():
    data = read_from(rel_file('REQUIREMENTS'))
    lines = map(lambda s: s.strip(), data.splitlines())
    return filter(None, lines)

def get_version():
    data = read_from(rel_file('hotwatch', '__init__.py'))
    return re.search(r"__version__ = '([^']+)'", data).group(1)


setup(    
    name             = 'hotwatch',
    author           = 'Richard Henry',
    author_email     = 'richardhenry@me.com',
    description      = 'HotWatch is a command line utility for monitoring the status of HotQueue queue instances.',
    license          = 'MIT',
    long_description = get_long_description(),
    install_requires = get_requirements(),
    packages         = ['hotwatch'],
    url              = 'http://github.com/richardhenry/hotwatch',
    version          = get_version(),
    classifiers      = [
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    entry_points     = {
        'console_scripts': ['hotwatch = hotwatch.cli:main'],
    },
)

