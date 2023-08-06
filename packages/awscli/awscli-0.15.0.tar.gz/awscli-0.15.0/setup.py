#!/usr/bin/env python

"""
distutils/setuptools install script.
"""

import os
import awscli

from setuptools import setup, find_packages


requires = ['botocore>=0.15.0,<0.16.0',
            'bcdoc>=0.7.0,<0.8.0',
            'six>=1.1.0',
            'colorama==0.2.5',
            'argparse>=1.1',
            'docutils>=0.10',
            'rsa==3.1.1']


setup(
    name='awscli',
    version=awscli.__version__,
    description='Universal Command Line Environment for AWS.',
    long_description=open('README.rst').read(),
    author='Mitch Garnaat',
    author_email='garnaat@amazon.com',
    url='http://aws.amazon.com/cli/',
    scripts=['bin/aws', 'bin/aws.cmd',
             'bin/aws_completer', 'bin/aws_zsh_completer.sh'],
    packages=find_packages('.', exclude=['tests*']),
    package_dir={'awscli': 'awscli'},
    package_data={'awscli': ['data/*.json', 'examples/*/*']},
    install_requires=requires,
    license=open("LICENSE.txt").read(),
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ),
)
