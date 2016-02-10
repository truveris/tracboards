# Copyright (c) 2016 Truveris, Inc. All Rights Reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

import os.path
from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, "README.rst")).read()
    CHANGES = open(os.path.join(here, "CHANGES.txt")).read()
except IOError:
    README = CHANGES = ""

setup(
    name="tracboards", version="0.2.0",
    description="Trac dashboards",
    long_description=README + "\n\n" + CHANGES,
    author="Truveris Inc.",
    author_email="engineering@truveris.com",
    url="http://github.com/truveris/tracboards",
    packages=find_packages(exclude=["*.tests*"]),
    include_package_data=True,
    license="ISC License",
    install_requires=[
    ],
    classifiers=[
        "License :: OSI Approved :: ISC License (ISCL)",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Framework :: Trac",
        "Topic :: Software Development :: Bug Tracking",
    ],
    entry_points = {
        "trac.plugins": [
            "tracboards = tracboards",
        ],
    },
)
