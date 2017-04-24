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
"""Configuration for WikiDP portal Flask app."""
import os

# TODO: template these values for flexible install
HOST = 'localhost'
LOG_ROOT = '/tmp/'

class BaseConfig(object):
    """Base / default config, no debug logging and short log format."""
    HOST = HOST
    DEBUG = False
    LOG_FORMAT = '[%(filename)-15s:%(lineno)-5d] %(message)s'
    LOG_FILE = LOG_ROOT + 'wikidp.log'

class DevConfig(BaseConfig):
    """Developer level config, with debug logging and long log format."""
    DEBUG = True
    LOG_FORMAT = '[%(levelname)-8s %(filename)-15s:%(lineno)-5d %(funcName)-30s] %(message)s'
    SECRET_KEY = '7d441f27d441f27567d441f2b6176a'

CONFIGS = {
    "dev": 'wikidp.config.DevConfig',
    "default": 'wikidp.config.BaseConfig'
}

def configure_app(app):
    """Grabs the environment variable for app config or defaults to dev."""
    config_name = os.getenv('WIKIDP_CONFIG', 'dev')
    app.config.from_object(CONFIGS[config_name])
