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
""" Flask application routes for Wikidata portal. """
import logging
from wikidp import APP

# Import Application Routes from '/routes' directory
from wikidp.routes.pages import *
from wikidp.routes.forms import *
from wikidp.routes.search import *
from wikidp.routes.api import *

from wikidp.utils import remove_extension_from_filename
@APP.template_filter('file_to_label')
def filter_file_to_label(filename):
    output = remove_extension_from_filename(filename)
    return output.replace('_', ' ').title()

if __name__ == "__main__":
    logging.debug("Running Flask App")
    APP.run(host='0.0.0.0')
