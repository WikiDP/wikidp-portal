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
""" Flask application for Wikidata portal. """
import logging
from wikidp import APP

# Import Routing converters
from wikidp.routing_converters import *

# Import Application Routes from '/routes' directory
from wikidp.routes.pages import *
from wikidp.routes.forms import *
from wikidp.routes.search import *
from wikidp.routes.api import *

# Import template filters
from wikidp.template_filters import *

if __name__ == "__main__":
    logging.debug("Running Flask App")
    APP.run(host='0.0.0.0',  port=APP.config.get('PORT'))
