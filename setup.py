#   Copyright 2020 The PyOSP Developers
#
#   Licensed under the Apache License, Version 2.0 (the "License")

import os
from os.path import realpath, dirname, join
from setuptools import setup, find_packages
import re

with open('README.md') as readme_file:
    readme = readme_file.read()

DISTNAME = "pyosp"
DESCRIPTION = "An Python Library fori Object-oriented Swath Profile Analysis"
AUTHOR = "Yichuan Zhu, Matthew A. Massey, Jason Dortch"
AUTHOR_EMAIL = "yichuan211@gmail.com"
URL = "https://github.com/PyOSP-devs/PyOSP.git"
LICENSE = "Apache License, Version 2.0"

classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: GIS/Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Operating System :: OS Independent",
]

PROJECT_ROOT = dirname(realpath(__file__))

# version
def get_version():
    VERSIONFILE = join("pyosp", "__init__.py")
    lines = open(VERSIONFILE, "rt").readlines()
    version_regex = r"^__version__ = ['\"]([^'\"]*)['\"]"
    for line in lines:
        mo = re.search(version_regex, line, re.M)
        if mo:
            return mo.group(1)
    raise RuntimeError("Unable to find version in %s." % (VERSIONFILE,))

# Get the long description from the README file
with open(join(PROJECT_ROOT, "README.md"), encoding="utf-8") as buff:
    LONG_DESCRIPTION = buff.read()

REQUIREMENTS_FILE = join(PROJECT_ROOT, "requirements.txt")

with open(REQUIREMENTS_FILE) as f:
    install_reqs = f.read().splitlines()

test_reqs = ["pytest"]

setup(
    name=DISTNAME,
    version=get_version(),
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    description=DESCRIPTION,
    license=LICENSE,
    url='https://github.com/PyOSP-devs/PyOSP.git',
    long_description=LONG_DESCRIPTION,
    long_description_content_type="text/x-rst",
    packages=find_packages(),
    include_package_data=True,
    package_data={"pyosp": 'datasets/*'},
    python_requires='>=3.5',
    install_requires=install_reqs,
    tests_require=test_reqs,
)
