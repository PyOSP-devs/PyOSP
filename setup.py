#   Copyright 2020 The PyOSP Developers
#
#   Licensed under the Apache License, Version 2.0 (the "License")

from os.path import realpath, dirname, join
from setuptools import setup, find_packages
import pyosp

with open('README.rst') as readme_file:
    readme = readme_file.read()

DISTNAME = "pyosp"
DESCRIPTION = "An Python Library for Objective-Oriented Swath Profile Analysis"
AUTHOR = "Yichuan Zhu, Matthew A. Massey, Jason Dortch"
AUTHOR_EMAIL = "yichuan.zhu@uky.edu"
URL = "https://github.com/PyOSP-devs/PyOSP.git"
LICENSE = "Apache License, Version 2.0"

classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: GIS/Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        "Operating System :: OS Independent",
]

PROJECT_ROOT = dirname(realpath(__file__))

# Get the long description from the README file
with open(join(PROJECT_ROOT, "README.rst"), encoding="utf-8") as buff:
    LONG_DESCRIPTION = buff.read()

REQUIREMENTS_FILE = join(PROJECT_ROOT, "requirements.txt")

with open(REQUIREMENTS_FILE) as f:
    install_reqs = f.read().splitlines()

test_reqs = ["pytest"]

setup(
	name=DISTNAME,
	version=pyosp.__version__,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    license=LICENSE,
    url='https://github.com/PyOSP-devs/PyOSP.git',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.5',
    install_requires=install_reqs,
    tests_require=test_reqs,
)
