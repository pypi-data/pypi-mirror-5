#!/usr/bin/env python

#   Xnt -- A Wrapper Build Tool
#   Copyright (C) 2013  Kenny Ballou

#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.

#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.

#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import shutil
from setuptools import setup, find_packages

xnt_version = os.path.join(os.path.abspath(
    os.path.dirname(__file__)), 'xnt', 'version.py')

exec(compile(open(xnt_version).read(), xnt_version, 'exec'))

def read(fname):
    return "\n" + open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="Xnt",
    version=__version__,
    author="Kenny Ballou",
    author_email="kennethmgballou@gmail.com",
    url="https://github.com/devnulltao/Xnt",
    description=("High-Level build script for doing more complex build tasks"),
    packages=find_packages(),
    test_suite="xnt.tests",
    scripts=["xnt/xenant.py",],
    package_data={
    },
    long_description=read("README.rst"),
    platforms=["Linux", "Windows",],
    entry_points={
        'console_scripts': [
            'xnt = xnt.xenant:main',
        ],
    },
    install_requires=['setuptools',],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows :: Windows 7',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development',
        'Topic :: Software Development :: Build Tools',
        'Topic :: Utilities',
    ],
)
