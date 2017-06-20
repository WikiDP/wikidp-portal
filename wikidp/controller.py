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
from flask import render_template
from flask import request
from wikidp import APP
from wikidp.model import FileFormat
from wikidp.lists import properties
import wikidp.DisplayFunctions as DF
OPTIONS = []
@APP.route("/browse")
def list_extensions():
    """Displays a list of extensions and media types."""
    formats = FileFormat.list_formats()
    return render_template('browse.html', formats=formats)

@APP.route("/")
def user_home(qid=False, string_search=True):
    """Main page for viewing, selecting, and updating items"""
    logging.debug("user_home for qid %s POST request and search string %s.", qid, string_search)
    global OPTIONS
    details = {}
    props = properties()
    if not qid:
        qid = (None, None)
        OPTIONS = []
    elif not string_search:
        details, _ = DF.item_detail_parse(qid)
        qid = (qid, DF.qid_label(qid))
    # Possibly just an else (havent run through contingencies)
    elif (string_search) and (qid != False):
        qid, OPTIONS, details, _ = DF.search_result(qid)

    return render_template('home.html', qid=qid, options=OPTIONS,
                           properties=props, details=details)

@APP.route("/", methods=['POST'])
def user_home_searched():
    """Routing after the user searches an item in a form"""
    logging.debug("Processing user POST request.")
    global OPTIONS
    # Currently hard code this to true, use a regex to indentify QIDs
    string_search = True
    qid = request.form['QID']
    if qid in [None, ""]:
        qid = "None"
    return user_home(qid, string_search)

@APP.route("/<qid>")
def selected_item(qid):
    """If the item ID is already known, the user can enter in the url"""
    qid = qid.strip()
	# print (qid)
    properties()
    return user_home(qid, string_search=False)
	# return render_template('user/home.html', qid = qid,
    #                        options=OPTIONS, properties=properties, details={})
    # do something with folder_name


if __name__ == "__main__":
    APP.run()
