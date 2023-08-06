#!/usr/bin/env python
#
# Copyright 2009 comger@gmail.com
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import distutils.core
import sys
# Importing setuptools adds some features like "setup.py develop", but
# it's optional so swallow the error if it's not there.
try:
    import setuptools
except ImportError:
    pass

kwargs = {}

version = "0.5.1.dev"

with open('README') as f:
    long_description = f.read()

distutils.core.setup(
    name="kpages",
    version=version,
    packages = ["kpages"],
    package_data = {},
    author="comger",
    author_email="comger@gmail.com",
    url="http://weibo.com/comger",
    license="http://www.apache.org/licenses/LICENSE-2.0",
    description="kpages is helper for you web app,redis mq,active on tornado, pymongo,redis,unittest,profile",
    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        ],
    long_description=long_description,
    setup_requires=['msgpack-python','pymongo','redis','termcolor','motor'],
    **kwargs
)
