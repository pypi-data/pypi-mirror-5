#!/bin/env python

import os
import re
#from distutils.core import setup
from setuptools import setup

VERSION_PATTERN = re.compile(r'^[^#]*__version__\W*\=\W*["\'](.*)["\']')
VERSION = None


def get_path(path):
    return os.path.join(os.path.dirname(__file__), path)


with file(get_path('smartfile/__init__.py')) as f:
    for line in f.xreadlines():
        m = VERSION_PATTERN.search(line)
        if m:
            VERSION = m.group(1)
            break

if VERSION is None:
    raise Exception('Could not parse version from module. Is __version__ '
                    'defined in __init__.py?')


name = 'smartfile'
release = '5'
versrel = VERSION + '-' + release
long_description = file(get_path('README.rst')).read()


setup(
    name=name,
    version=versrel,
    description='A Python client for the SmartFile API.',
    long_description=long_description,
    install_requires=[
        'oauthlib',
        'requests',
        'requests_oauthlib',
    ],
    author='SmartFile',
    author_email='info@smartfile.com',
    maintainer='Ben Timby',
    maintainer_email='btimby@gmail.com',
    url='http://github.com/smartfile/client-python/',
    license='MIT',
    packages=['smartfile'],
    package_data={'': ['README.rst']},
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ),
)
