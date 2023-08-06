#!/usr/bin/env python

from setuptools import setup

def linelist(text):
    """
    Returns each non-blank line in text enclosed in a list.
    """
    return [ l.strip() for l in text.strip().splitlines() if l.strip() ]
    

setup(
    name='simplere',
    version='1.0.2',
    author='Jonathan Eunice',
    author_email='jonathan.eunice@gmail.com',
    description='Simpler, cleaner access to regular expressions. Globs too.',
    long_description=open('README.rst').read(),
    url='https://bitbucket.org/jeunice/simplere',
    packages=['simplere'],
    install_requires=['mementos'],
    tests_require = ['tox', 'pytest'],
    zip_safe = False,  # actually it is, but this apparently avoids setuptools hacks
    keywords='re regex regular expression glob',
    classifiers=linelist("""
        Development Status :: 4 - Beta
        Operating System :: OS Independent
        License :: OSI Approved :: BSD License
        Intended Audience :: Developers
        Programming Language :: Python
        Programming Language :: Python :: 2.6
        Programming Language :: Python :: 2.7
        Programming Language :: Python :: 3
        Programming Language :: Python :: 3.2
        Programming Language :: Python :: 3.3
        Programming Language :: Python :: Implementation :: CPython
        Programming Language :: Python :: Implementation :: PyPy
        Topic :: Software Development :: Libraries :: Python Modules
    """)
)
