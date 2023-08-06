#!/usr/bin/env python
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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Setup file for bitmask.
"""

from __future__ import print_function

import sys

if not sys.version_info[0] == 2:
    print("[ERROR] Sorry, Python 3 is not supported (yet). "
          "Try running with python2: python2 setup.py ...")
    exit()

try:
    from setuptools import setup, find_packages
except ImportError:
    from pkg import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages
import os

from pkg import utils

import versioneer
versioneer.versionfile_source = 'src/leap/bitmask/_version.py'
versioneer.versionfile_build = 'leap/bitmask/_version.py'
versioneer.tag_prefix = ''  # tags are like 1.2.0
versioneer.parentdir_prefix = 'leap.bitmask-'

#from setuptools import Command

# The following import avoids the premature unloading of the `util` submodule
# when running tests, which would cause an error when nose finishes tests and
# calls the exit function of the multiprocessing module.
from multiprocessing import util
assert(util)

setup_root = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(setup_root, "src"))

trove_classifiers = [
    "Development Status :: 3 - Alpha",
    "Environment :: X11 Applications :: Qt",
    "Intended Audience :: End Users/Desktop",
    ("License :: OSI Approved :: GNU General "
     "Public License v3 or later (GPLv3+)"),
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.6",
    "Programming Language :: Python :: 2.7",
    "Topic :: Communications",
    "Topic :: Security",
    "Topic :: System :: Networking",
    "Topic :: Utilities"
]


parsed_reqs = utils.parse_requirements()

cmdclass = versioneer.get_cmdclass()
leap_launcher = 'bitmask=leap.bitmask.app:main'

from setuptools.command.develop import develop as _develop


def copy_reqs(path, withsrc=False):
    # add a copy of the processed requirements to the package
    _reqpath = ('leap', 'bitmask', 'util', 'reqs.txt')
    if withsrc:
        reqsfile = os.path.join(path, 'src', *_reqpath)
    else:
        reqsfile = os.path.join(path, *_reqpath)
    print("UPDATING %s" % reqsfile)
    if os.path.isfile(reqsfile):
        os.unlink(reqsfile)
    with open(reqsfile, "w") as f:
        f.write('\n'.join(parsed_reqs))


class cmd_develop(_develop):
    def run(self):
        # versioneer:
        versions = versioneer.get_versions(verbose=True)
        self._versioneer_generated_versions = versions
        # unless we update this, the command will keep using the old version
        self.distribution.metadata.version = versions["version"]

        _develop.run(self)
        copy_reqs(self.egg_path)

cmdclass["develop"] = cmd_develop

# next two classes need to augment the versioneer modified ones

versioneer_build = cmdclass['build']
versioneer_sdist = cmdclass['sdist']


class cmd_build(versioneer_build):
    def run(self):
        versioneer_build.run(self)
        copy_reqs(self.build_lib)


class cmd_sdist(versioneer_sdist):
    def run(self):
        return versioneer_sdist.run(self)

    def make_release_tree(self, base_dir, files):
        versioneer_sdist.make_release_tree(self, base_dir, files)
        copy_reqs(base_dir, withsrc=True)


cmdclass["build"] = cmd_build
cmdclass["sdist"] = cmd_sdist

import platform
_system = platform.system()
IS_LINUX = True if _system == "Linux" else False

data_files = []

if IS_LINUX:
    # XXX use check_for_permissions to install data
    # globally. See #3805
    data_files = [
        ("share/polkit-1/actions",
         ["pkg/linux/polkit/net.openvpn.gui.leap.policy"]),
        ("etc/leap/",
         ["pkg/linux/resolv-update"]),
    ]

setup(
    name="leap.bitmask",
    package_dir={"": "src"},
    version=versioneer.get_version(),
    cmdclass=cmdclass,
    description="The Internet Encryption Toolkit",
    long_description=(
        "Desktop Client for the LEAP Platform."
        "\n"
        "LEAP (LEAP Encryption Access Project) develops "
        "a multi-year plan to secure everyday communication, breaking down"
        "into discrete services, to be rolled out one at a time.\n"
        "The client for the current phase gives support to the EIP Service."
        "EIP (the Encrypted Internet Proxy) provides circumvention, location "
        "anonymization, and traffic "
        "encryption in a hassle-free, automatically self-configuring fashion, "
        "and has an enhanced level of security."
    ),
    classifiers=trove_classifiers,
    install_requires=parsed_reqs,
    test_suite='nose.collector',
    tests_require=utils.parse_requirements(
        reqfiles=['pkg/requirements-testing.pip']),
    keywords=('Bitmask, LEAP, client, qt, encryption, '
              'proxy, openvpn, imap, smtp'),
    author='The LEAP Encryption Access Project',
    author_email='info@leap.se',
    url='https://leap.se',
    license='GPL-3+',
    packages=find_packages(
        'src',
        exclude=['ez_setup', 'setup', 'examples', 'tests']),
    namespace_packages=["leap"],
    package_data={'': ['util/*.txt']},
    include_package_data=True,
    # not being used? -- setuptools does not like it.
    # looks like debhelper is honoring it...
    data_files=data_files,
    zip_safe=False,
    platforms="all",
    entry_points={
        'console_scripts': [leap_launcher]
    },
)
