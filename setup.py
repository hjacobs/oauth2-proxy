#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import inspect
import os
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

version = '0.2'

__location__ = os.path.join(os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe())))


def get_install_requirements(path):
    content = open(os.path.join(__location__, path)).read()
    return [req for req in content.split('\\n') if req != '']


class PyTest(TestCommand):
    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.cov = None
        self.pytest_args = ['--cov', 'oauth2_proxy', '--cov-report', 'term-missing']

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest

        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='oauth2-proxy',
    packages=find_packages(),
    version=version,
    description='OAuth2 proxy with authorization/redirect flow',
    long_description=open('README.rst').read(),
    author='Zalando SE',
    url='https://github.com/zalando-stups/oauth2-proxy',
    keywords='oauth flask proxy serve',
    license='Apache License Version 2.0',
    install_requires=get_install_requirements('requirements.txt'),
    tests_require=['pytest-cov', 'pytest', 'mock'],
    cmdclass={'test': PyTest},
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.4',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ]
)
