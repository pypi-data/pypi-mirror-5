#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement, division, absolute_import


try:
    from setuptools import setup, Command
except ImportError:
    from distutils.core import setup, Command


def get_version():
    """Get current version from VERSION file"""
    with open("VERSION") as f:
        return f.readline().strip()


def get_description():
    """Get current package description"""
    with open("DESCRIPTION") as f:
        return f.read()


def main():
    __version__ = get_version()
    __description__ = get_description()

    setup(
        name='Flask-JqueryUiBootstrap',
        version=__version__,
        author="Arkadiusz Tułodziecki",
        author_email="atulodzi@gmail.com",
        description=__description__,
        long_description=open('README.rst').read() + '\n\n' + open('HISTORY.rst').read(),
        license="MIT",
        url="https://github.com/lightningwolf/Flask-JqueryUiBootstrap",
        packages=['flask_jqueryuibootstrap'],
        zip_safe=False,
        include_package_data=True,
        platforms=['any'],
        install_requires=[
            'Flask>=0.8'
        ],
        classifiers=[
            "Development Status :: 3 - Alpha",
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'Natural Language :: Polish',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Software Development :: Libraries :: Python Modules'
        ],
    )


if __name__ == '__main__':
    main()