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
from flask import Flask
from wikidata import wikidata_test
app = Flask(__name__)

@app.route("/")
def home():
    """ Home route. """
    text = wikidata_test()
    return text

if __name__ == "__main__":
    app.run()
