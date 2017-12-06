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

@APP.route("/about")
def about():
    """Rendering the about page"""
    return render_template('about.html')

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

@APP.route("/contribute", methods=['POST'])
def contribute_selected_page():
    options = json.loads(request.form['optionList'])
    previewItem = DF.item_detail_parse(request.form['qid'])
    return render_template('contribute.html', selected=previewItem, options=options)

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

@APP.route("/api-get-qid-label", methods=['POST'])
def api_get_qid_label():
    """User posts a item-id and returns json of (id, label, description, aliases)"""
    logging.debug("Processing user POST request.")
    qid = request.form['qid'] 
    output = DF.qid_to_basic_details(qid)
    return json.dumps(output)

@APP.route("/api-lookup-item", methods=['POST'])
def api_lookup_item():
    """User posts a string and returns list of json of (id, label, description, aliases)"""
    logging.debug("Processing user POST request.")
    string = request.form['string'].strip()
    output = DF.search_result_list(string)
    return json.dumps(output)

if __name__ == "__main__":
    APP.run()
