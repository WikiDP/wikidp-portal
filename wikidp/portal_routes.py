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
from wikidata import get_formats_generator
app = Flask(__name__)

@app.route("/")
def hello():
    """ Home route. """
    formats = get_formats_generator()
    format_list = []
    for file_format in formats:
        format_list.append(str(file_format))
    return "\n".join(format_list)

if __name__ == "__main__":
    app.run()
