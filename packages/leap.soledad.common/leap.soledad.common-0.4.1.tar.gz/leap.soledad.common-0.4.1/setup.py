# -*- coding: utf-8 -*-
# setup.py
# Copyright (C) 2013 LEAP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
setup file for leap.soledad.common
"""
from setuptools import setup
from setuptools import find_packages

import versioneer
versioneer.versionfile_source = 'src/leap/soledad/common/_version.py'
versioneer.versionfile_build = 'leap/soledad/common/_version.py'
versioneer.tag_prefix = ''  # tags are like 1.2.0
versioneer.parentdir_prefix = 'leap.soledad.common-'

from pkg import utils

trove_classifiers = (
    "Development Status :: 3 - Alpha",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: "
    "GNU General Public License v3 or later (GPLv3+)",
    "Environment :: Console",
    "Operating System :: OS Independent",
    "Operating System :: POSIX",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Topic :: Database :: Front-Ends",
    "Topic :: Software Development :: Libraries :: Python Modules"
)

# XXX add ref to docs

setup(
    name='leap.soledad.common',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    url='https://leap.se/',
    license='GPLv3+',
    description='Synchronization of locally encrypted data among devices '
                '(common files).',
    author='The LEAP Encryption Access Project',
    author_email='info@leap.se',
    long_description=(
        "Soledad is the part of LEAP that allows application data to be "
        "securely shared among devices. It provides, to other parts of the "
        "LEAP project, an API for data storage and sync."
    ),
    classifiers=trove_classifiers,
    namespace_packages=["leap", "leap.soledad"],
    packages=find_packages('src', exclude=['leap.soledad.common.tests']),
    package_dir={'': 'src'},
    test_suite='leap.soledad.common.tests',
    install_requires=utils.parse_requirements(),
    tests_require=utils.parse_requirements(
        reqfiles=['pkg/requirements-testing.pip']),
    extras_require={
        'couchdb': ['couchdb'],
    },
)
