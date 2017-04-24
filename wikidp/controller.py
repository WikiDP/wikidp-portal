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
from flask import render_template
from wikidp import APP
from wikidp.model import FileFormat

@APP.route("/")
def list_extensions():
    """Displays a list of extensions and media types."""
    formats = FileFormat.list_formats()
    return render_template('home.html', formats=formats)

if __name__ == "__main__":
    APP.run()
