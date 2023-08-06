#-------------------------------------------------------------------------------
# pss: setup.py
#
# Setup/installation script.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in the public domain
#-------------------------------------------------------------------------------
import os, sys
from distutils.core import setup


try:
    with open('README.rst', 'rt') as readme:
        description = '\n' + readme.read()
except IOError:
    # maybe running setup.py from some other dir
    description = ''


setup(
    # metadata
    name='pss',
    description='Tool for grepping through source code',
    long_description=description,
    license='Public domain',
    version='1.39',
    author='Eli Bendersky',
    maintainer='Eli Bendersky',
    author_email='eliben@gmail.com',
    url='https://github.com/eliben/pss',
    platforms='Cross Platform',
    classifiers = [
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',],

    packages=['psslib', 'psslib.colorama'],

    scripts=['scripts/pss.py', 'scripts/pss'],
)

