#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
setup file for python project.
"""

from setuptools import setup, find_packages

SRC_DIR = 'src'
VERSION = '0.1'
README = ''

with open('README.md') as f:
    README = f.read()

setup(
    name='SimpleCFS',
    version=VERSION,
    description="Simple Coded File System",
    long_description=README,
    author="lijian",
    author_email="hustlijian@gmail.com",
    license="Apache License 2.0",
    url="TODO",
    keywords=' '.join([
        'python',
        'filesystem',
        'distributed',
        'erasure code',
    ]),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Programming Language :: Python',
        'Programming Language :: C',
        'Topic :: System :: Filesystems',
    ],
    package_dir={'': SRC_DIR},
    packages=find_packages(SRC_DIR),
    include_package_data=True,
)
