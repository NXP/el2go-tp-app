#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# Copyright 2023 NXP
#
# SPDX-License-Identifier: BSD-3-Clause

"""The setup script."""

from setuptools import find_packages, setup

with open("README.rst") as readme_file:
    readme = readme_file.read()

with open("HISTORY.rst") as history_file:
    history = history_file.read()

requirements = ["Click>=8.0", "spsdk<2"]

test_requirements = [
    "pytest>=3",
]

setup(
    author="NXP Semiconductors",
    author_email="",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    description="Standalone SPSDK-like application used to communicate with EL2GO NXP Provisioning Firmware.",
    entry_points={
        "console_scripts": [
            "el2go_tp_app=el2go_tp_app.cli:safe_main",
        ],
    },
    install_requires=requirements,
    license="BSD license",
    long_description=readme + "\n\n" + history,
    include_package_data=True,
    keywords="el2go_tp_app",
    name="el2go_tp_app",
    packages=find_packages(include=["el2go_tp_app", "el2go_tp_app.*"]),
    test_suite="tests",
    tests_require=test_requirements,
    url="https://github.com/NXP/el2go-tp-app",
    version="1.0.0",
    zip_safe=False,
)
