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

from wikidp import APP
from wikidp.wikidata import test_query

@APP.route("/")
def home():
    test_query()
    return "Hello"

if __name__ == "__main__":
    APP.run()
