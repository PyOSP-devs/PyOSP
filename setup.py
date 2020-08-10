#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
import pyosp

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=7.0', ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="Yichuan Zhu",
    author_email='yichuan211@gmail.com',
    python_requires='>=3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="An Python Library for Objective-Oriented Swath Profile Analysis",
    version=pyosp.__version__,
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=read('README.rst'),
    include_package_data=True,
    keywords='pyosp',
    name='pyosp',
    packages=find_packages(include=['pyosp', 'pyosp.*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/yzh211/PyOSP.git',
)
