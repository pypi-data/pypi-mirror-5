#!/usr/bin/env python
from setuptools import setup
import pycli_tools

setup(
    name = 'pycli_tools',
    version = pycli_tools.__version__,
    packages = [
        'pycli_tools'
    ],
    download_url = 'https://github.com/nrocco/pycli-tools/tags',
    url = 'http://nrocco.github.io/',
    author = pycli_tools.__author__,
    author_email = 'dirocco.nico@gmail.com',
    description = 'A python module to help create predictable command line tools',
    long_description = pycli_tools.__doc__,
    include_package_data = True,
    classifiers = [
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
