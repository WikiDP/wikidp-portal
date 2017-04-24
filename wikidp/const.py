#!/usr/bin/python
# coding=UTF-8
#
# WikiDP Wikidata Portal
# Copyright (C) 2017
# All rights reserved.
#
# This code is distributed under the terms of the GNU General Public
# License, Version 3. See the text file "COPYING" for further details
# about the terms of this license.
#
"""Constants used across BitCurator modules.
These need to map to the names used in the default config file, but better
than multiple hardcoded strings in code.
"""

class ConfKey(object):
    """Config key string constatnts"""
    LOG_FORMAT = 'LOG_FORMAT'
    LOG_FILE = 'LOG_FILE'
