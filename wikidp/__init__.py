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
# This is a python __init__ script to create the app and import the
# main package contents
"""Initialisation module for package, kicks of the flask app."""
import logging
import os
from getpass import getpass

from flask import Flask
# Load the application
APP = Flask(__name__)

from wikidp.config import configure_app
from wikidp.const import ConfKey
# Get the appropriate config
configure_app(APP)
# Configure logging across all modules
logging.basicConfig(filename=APP.config[ConfKey.LOG_FILE], level=logging.DEBUG,
                    format=APP.config[ConfKey.LOG_FORMAT])
logging.info("Started Wiki-DP Portal app.")
logging.debug("Configured logging.")
logging.debug("Logging in directory %s", APP.config[ConfKey.LOG_FILE])
logging.debug("Application configured with languages=%s", APP.config[ConfKey.WIKIBASE_LANGUAGE])

# Checking for user-config.py
try:
    with open('user-config.py') as file:
        logging.info("user-config.py available")
except IOError:
    template_username = '<username>'
    template_password = '<password>'
    # generate the user-config.py based on keyboard prompts if not exist
    logging.info("user-config.py unavailable")
    user_username = APP.config.get('WIKIDATA_USER_NAME')
    if not user_username or user_username == template_username:
        user_username = input('What is your Wikimedia Username? ')
    user_password = APP.config.get('WIKIDATA_PASSWORD')
    if not user_password or user_password == template_password:
        user_password = getpass(prompt='What is your Wikimedia Password? ')
    with open('user-config.py.template', 'r') as template:
        logging.info("user-config.py available")
        data=template.read().replace('<username>', user_username)\
                            .replace('<password>', user_password)
        new_file = open("user-config.py","w+")
        new_file.write(data)
        new_file.close()

# Import the application routes
logging.info("Setting up application routes")
import wikidp.run
