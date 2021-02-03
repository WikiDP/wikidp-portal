#!/usr/bin/python
# coding=UTF-8
#
# WikiDP Wikidata Portal
# Copyright (C) 2020
# All rights reserved.
#
# This code is distributed under the terms of the GNU General Public
# License, Version 3. See the text file "COPYING" for further details
# about the terms of this license.
#
"""Configuration for WikiDP portal Flask app."""
import logging
import os
import tempfile

from flask import Flask

from wikidp.const import ConfKey


# Template these values for flexible install
HOST = 'localhost'
TEMP = tempfile.gettempdir()


# pylint: disable=R0903
class BaseConfig:
    """Base / default config, no debug logging and short log format."""

    CACHE_DIR = os.path.join(TEMP, 'caches')
    DEBUG = False
    HOST = HOST
    ITEM_REGEX = r'(Q|q)\d+'
    MEDIAWIKI_API_URL = "https://www.wikidata.org/w/api.php"
    OAUTH_MEDIAWIKI_URL = "https://www.mediawiki.org/w/index.php"
    SPARQL_ENDPOINT_URL = "https://query.wikidata.org/sparql"
    # Bind to PORT if defined, otherwise default to 5000.
    PORT = int(os.environ.get('PORT', 5000))
    PROPERTY_REGEX = r'(P|p)\d+'
    LOG_FILE = os.path.join(TEMP, 'wikidp.log')
    LOG_FORMAT = '[%(filename)-15s:%(lineno)-5d] %(message)s'
    SECRET_KEY = '7d441f27d441f27567d441f2b6176a'
    WIKIBASE_LANGUAGE = os.getenv('WIKIBASE_LANGUAGE', 'en')
    WIKIDATA_FB_LANG = os.getenv('WIKIDP_FB_LANG', 'en')
    WIKIDATA_LANG = os.getenv('WIKIDP_LANG', 'en')
    WIKIDATA_PASSWORD = os.getenv('WIKIDP_BOT_PASSWORD', '<password>')
    WIKIDATA_USER_NAME = os.getenv('WIKIDP_BOT_USER', '<username>')
    WIKIDP_CONSUMER_KEY = os.environ.get('WIKIDP_CONSUMER_KEY', '')
    WIKIDP_CONSUMER_SECRET = os.environ.get('WIKIDP_CONSUMER_SECRET', '')
    USER_AGENT = os.environ.get(
        'USER_AGENT',
        'wikidp-portal/0.0 (https://www.wikidp.org/; admin@wikidp.org)'
    )


# pylint: disable=R0903
class DevConfig(BaseConfig):
    """Developer level config, with debug logging and long log format."""

    DEBUG = True
    LOG_FORMAT = '[%(asctime)s %(levelname)-8s %(filename)-15s:%(lineno)-5d ' +\
                 '%(funcName)-30s] %(message)s'
    MEDIAWIKI_API_URL = "https://wikidp.wiki.opencura.com/w/api.php"
    SPARQL_ENDPOINT_URL = 'https://wikidp.wiki.opencura.com/query/sparql'


CONFIGS = {
    "dev": 'wikidp.config.DevConfig',
    "default": 'wikidp.config.BaseConfig'
}


def configure_app(app):
    """Grab the environment variable for app config or defaults to dev."""
    config_name = os.getenv('WIKIDP_CONFIG', 'default')
    app.config.from_object(CONFIGS[config_name])
    app.config[ConfKey.STATIC_DIR] = os.path.join(app.root_path, 'static')
    if os.getenv('WIKIDP_CONFIG_FILE'):
        app.config.from_envvar('WIKIDP_CONFIG_FILE')
    app.config['WIKIDATA_SIGN_UP_URL'] = \
        "https://www.wikidata.org/w/index.php?title=Special:CreateAccount"
    _lang = app.config[ConfKey .WIKIDATA_LANG]
    _fb_lang = app.config[ConfKey.WIKIDATA_FB_LANG]
    # Create the list of unique languages to easy SPARQL queries
    if _lang != _fb_lang:
        app.config[ConfKey.WIKIBASE_LANGUAGE] = f"{_lang},{_fb_lang}"


APP = Flask(__name__)
# Get the appropriate config
configure_app(APP)
# Configure logging across all modules
logging.basicConfig(filename=APP.config[ConfKey.LOG_FILE], level=logging.DEBUG,
                    format=APP.config[ConfKey.LOG_FORMAT])
logging.info("Started Wiki-DP Portal app.")
logging.debug("Configured logging.")
logging.debug("Logging in directory %s", APP.config[ConfKey.LOG_FILE])
logging.debug("Application configured with languages=%s",
              APP.config[ConfKey.WIKIBASE_LANGUAGE])
