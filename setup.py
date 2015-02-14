from __future__ import print_function

import sys
import os
from os.path import join, abspath, dirname

from setuptools import setup
from setuptools.command.test import test

import ec2ingress

here_dir = abspath(dirname(__file__))

if sys.version_info < (2, 7):
    error = "ERROR: Python Version 2.7 or above is required. Exiting."
    print(error, file=sys.stderr)
    sys.exit(1)


def read(*filenames):
    buf = []
    for filename in filenames:
        with open(os.path.join(here_dir, filename)) as f:
            buf.append(f.read())
    return '\n\n'.join(buf)


def get_requirements():
    with open(join(here_dir, 'requirements.txt')) as f:
        reqs = f.read().splitlines()
        print('requirements: %s' % (reqs,))
        return reqs


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
    name='ec2ingress',
    version=ec2ingress.__version__,
    license='http://www.opensource.org/licenses/mit-license.php',
    url='https://github.com/eukaryote/ec2ssh',
    description='Control SSH Access to EC2 instances',
    long_description=read('README.rst', 'CHANGES.rst'),
    keywords='aws ec2 ssh',
    author='Calvin Smith',
    author_email='sapientdust+ec2ssh@gmail.com',
    packages=[ec2ingress.__name__],
    platforms='any',
    cmdclass={'test': PyTest},
    install_requires=get_requirements(),
    tests_require=['pytest'],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            '{name} = {name}.main:main'.format(name=ec2ingress.__name__),
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
