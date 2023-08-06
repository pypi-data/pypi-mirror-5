#!/usr/bin/env python

from setuptools import setup, find_packages

name = "indicsyllabifier"

setup(
    name = name,
    version = "0.3",
    url = "http://silpa.org.in/Syllabize",
    license = "LGPL-3.0",
    description =  "Syllabify each word in the given text",
    author = "Santhosh Thottingal",
    author_email = "santhosh.thottingal@gmail.com",
    long_description =   "Syllabify each word in the given text",
    packages = find_packages('.'),
    package_data = {'.':[]},
    include_package_data = True,
    setup_requires = ['setuptools-git'],
    install_requires = ['setuptools','silpa_common'],
    test_suite='tests',
    zip_safe = False,
    )
