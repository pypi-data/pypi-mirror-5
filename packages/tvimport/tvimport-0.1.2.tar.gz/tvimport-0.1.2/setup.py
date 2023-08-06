#!/usr/bin/env python
from setuptools import setup
import os
import sys

needed_pkgs = []
needed_pkgs.append('pyinotify')
needed_pkgs.append('tvdb_api')

from distutils.core import setup

setup(name='tvimport',
    version='0.1.2',
    description='Daemon to automatically organize tv series',
    author='luca Gasperini',
    author_email='luca.gasperini@gmail.com',
    url='https://github.com/LucaGas/tvimport',
    packages=['tvimport'],

install_requires = needed_pkgs,

    )
	
