from __future__ import print_function

import codecs
import sys
import os
from os.path import join, abspath, dirname
import re

from setuptools import setup
from setuptools.command.test import test

HERE_DIR = abspath(dirname(__file__))
NAME = 'ec2ingress'


if sys.version_info < (2, 7):
    msg = "ERROR: Python Version 2.7 or above is required. Exiting."
    print(msg, file=sys.stderr)
    sys.exit(1)


def read(*filenames):
    buf = []
    for filename in filenames:
        with codecs.open(os.path.join(HERE_DIR, filename), 'r') as f:
            buf.append(f.read())
    return '\n\n'.join(buf)


def find_version(*filenames):
    version_file = read(os.path.join(*filenames))
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


def get_requirements():
    with open(join(HERE_DIR, 'requirements.txt')) as f:
        return f.read().splitlines()


class PyTest(test):

    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


setup(
    name=NAME,
    version=find_version(NAME, '__init__.py'),
    license='http://www.opensource.org/licenses/mit-license.php',
    url='https://github.com/eukaryote/ec2ssh',
    description='Control SSH Access to EC2 instances',
    long_description=read('README.rst', 'CHANGES.rst'),
    keywords='aws ec2 ssh',
    author='Calvin Smith',
    author_email='sapientdust+ec2ssh@gmail.com',
    packages=[NAME],
    platforms='any',
    cmdclass={'test': PyTest},
    install_requires=get_requirements(),
    tests_require=['pytest'],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            '{name} = {name}.main:main'.format(name=NAME),
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Environment :: Console',
        'Development Status :: 4 - Beta',
        'Topic :: Security',
        'Topic :: Utilities'
    ],
)
