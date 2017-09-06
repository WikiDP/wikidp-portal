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
from flask import render_template, request, json
from wikidp import APP
from wikidp.model import FileFormat
from wikidp.lists import properties
import wikidp.DisplayFunctions as DF

@APP.route("/")
def welcome():
    """Landing Page for first time"""
    return render_template('welcome.html')

@APP.route("/browse")
def list_extensions():
    """Displays a list of extensions and media types."""
    formats = FileFormat.list_formats()
    return render_template('browse.html', formats=formats)


@APP.route("/search", methods=['POST'])
def search_results_page():
    # print (request.form['userInput'].strip())
    options = DF.search_result_list(request.form['userInput'].strip())
    # print (options)
    return render_template('search_results.html', options=options)

@APP.route("/preview", methods=['POST'])
def preview_selected_page():
    options = json.loads(request.form['optionList'])
    previewItem = DF.item_detail_parse(request.form['qid'])
    return render_template('preview-item.html', selected=previewItem, options=options)

@APP.route("/<qid>")
def selected_item(qid):
    """If the item ID is already known, the user can enter in the url, not yet functioning"""
    qid = qid.strip()
	# print (qid)
    properties()
    return preview_selected_page()

@APP.route("/api-load-item", methods=['POST'])
def api_load_item():
    """Routing after the user searches an item in a form"""
    logging.debug("Processing user POST request.")
    qid = request.form['qid'] 
    if qid in [None, ""]:
        qid = "None"
        return "error, item not found"
    output = DF.item_detail_parse(qid)
    # print (output)
    return json.dumps(output)


if __name__ == "__main__":
    APP.run()
