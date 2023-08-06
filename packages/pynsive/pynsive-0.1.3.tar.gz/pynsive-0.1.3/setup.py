# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
    from setuptools.command import easy_install
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages
    from setuptools.command import easy_install

import sys
from os import path
from distutils.core import setup
from distutils.extension import Extension


def read(relative):
    contents = open(relative, 'r').read()
    return [l for l in contents.split('\n') if l != '']


def ez_install(package):
    easy_install.main(["-U", package])


setup(
    name='pynsive',
    version='0.1.3',
    description=("""A Python plugin and introspection library prounounced,
"pensive." This library allows a developer to introduce plugins via PEP 302
and allows for class searching via type and inheritance introspections.
"""),
    author='John Hopper',
    author_email='john.hopper@jpserver.net',
    url='https://github.com/zinic/pynsive',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Environment :: Plugins',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3'
    ],
    tests_require=read('./tools/test-requires'),
    install_requires=read('./tools/install-requires'),
    test_suite='nose.collector',
    zip_safe=False,
    include_package_data=True,
    packages=find_packages(exclude=['ez_setup']))
