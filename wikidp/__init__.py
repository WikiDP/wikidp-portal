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

from flask import Flask
from wikidp.config import configure_app
from wikidp.const import ConfKey
# Load the application
APP = Flask(__name__)

# Get the appropriate config
configure_app(APP)

# Configure logging across all modules

logging.basicConfig(filename=APP.config[ConfKey.LOG_FILE], level=logging.DEBUG,
                    format=APP.config[ConfKey.LOG_FORMAT])
logging.info("Started Wiki-DP Portal app.")
logging.debug("Configured logging.")

# Import the application routes
logging.info("Setting up application routes")
import wikidp.portal_routes
