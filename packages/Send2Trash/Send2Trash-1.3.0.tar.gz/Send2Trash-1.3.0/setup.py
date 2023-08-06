import sys
import os.path as op

from setuptools import setup

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: BSD License',
    'Operating System :: MacOS :: MacOS X',
    'Operating System :: Microsoft :: Windows',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Topic :: Desktop Environment :: File Managers',
]

LONG_DESCRIPTION = open('README.rst', 'rt').read() + '\n\n' + open('CHANGES.rst', 'rt').read()

setup(
    name='Send2Trash',
    version='1.3.0',
    author='Hardcoded Software',
    author_email='hsoft@hardcoded.net',
    packages=['send2trash'],
    scripts=[],
    url='http://github.com/hsoft/send2trash',
    license='BSD License',
    description='Send file to trash natively under Mac OS X, Windows and Linux.',
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
)