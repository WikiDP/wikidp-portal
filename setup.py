#!/usr/bin/python
# coding=UTF-8
#
# BitCurator Access Webtools (Disk Image Access for the Web)
# Copyright (C) 2014 - 2016
# All rights reserved.
#
# This code is distributed under the terms of the GNU General Public
# License, Version 3. See the text file "COPYING" for further details
# about the terms of this license.
#
"""Setup for flask app."""
from setuptools import setup

setup(
    name='wikidp',
    packages=['wikidp'],
    include_package_data=True,
    install_requires=[
        'Flask==1.0.2',
        'wikidataintegrator',
        'lxml==4.3.0',
        'pandas',
        'pywikibot',
        'pylint',
        'pytest',
        'pytest-cov',
        'tqdm',
        'validators==0.12.4'
        #
        # carl@openpreservation.org removed these dependencies as almost certainly
        # unused on 2nd Oct 2017, commenting for safety.
        # 'wtforms',
        # 'requests==2.13.0',
        # 'simplejson==3.10.0',
    ],
)

#TO DO: If using python3.6, I had to run 'install certificates.command' inside the directory in order to load url's
