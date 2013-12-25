#!/usr/bin/env python

from distutils.core import setup

execfile('modules/subfinder/version.py')

setup(name='subfinder',
    version=__version__,
    description='Tool to fetch subs from OpenSubtitles',
    author=__maintainer__,
    download_url='https://github.com/fim/subfinder/tarball/master',
    package_dir = {'': 'modules'},
    packages=['subfinder'],
    scripts=['subfinder']
)
