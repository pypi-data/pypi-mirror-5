##############################################################################
#
# Copyright (c) Zope Corporation.  All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE
#
##############################################################################
name = 'zc.zrs'
version = '2.4.2'

from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

import os, shutil
if os.path.isdir('build'):
    shutil.rmtree('build')

entry_points = """
[console_scripts]
zrsmonitor-script = zc.zrs.monitor:main
last-zeo-transaction = zc.zrs.last:main
"""

tests_require = ['zope.testing', 'zc.zk [static]', 'mock']

long_description = open('README.rst').read()

setup(
    name = name,
    long_description = long_description,
    description = long_description.split('\n')[1],
    version = version,
    author = "Jim Fulton",
    author_email = "jim#zope.com",
    license = "ZPL 2.1",
    keywords = "ZODB",

    packages = ['zc', 'zc.zrs'],
    include_package_data = True,
    data_files = [('.', ['README.txt'])],
    zip_safe = True,
    entry_points = entry_points,
    package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = [
        'setuptools',
        'ZODB3',
        'Twisted',
        ],
    extras_require = dict(test=tests_require),
    tests_require = tests_require,
    test_suite = 'zc.zrstests.tests.test_suite',
    )
