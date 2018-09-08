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
import re

from flask import render_template, request, json, redirect
from wikidp import APP
from wikidp.const import ConfKey
from wikidp.model import FileFormat, PuidSearchResult
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

@APP.route("/reports")
def reports():
    """Rendering the reports page"""
    return render_template('reports.html')

@APP.route("/browse")
def list_extensions():
    """Displays a list of extensions and media types."""
    formats = FileFormat.list_formats(lang = APP.config[ConfKey.WIKIBASE_LANGUAGE])
    return render_template('browse.html', formats=formats)

@APP.route("/puid/<string:puid>")
def search_puid(puid):
    """Displays a list of extensions and media types."""
    puid = puid.replace('_', '/')
    logging.debug("Searching for PUID: %s", puid)
    results = PuidSearchResult.search_puid(puid, lang = APP.config[ConfKey.WIKIBASE_LANGUAGE])
    return render_template('puid_results.html', results=results, puid=puid)

@APP.route("/search", methods=['POST'])
def process_search_url():
    """Processes search request into a state-saving url."""
    return redirect('/search?string='+request.form['userInput'].strip())

@APP.route("/search")
def search_results_page():
    """Displays the most likely results of a users search."""
    _input = request.args.get('string', default = 0, type = str)
    # Check if searching with PUID
    try:
        if re.search("[x-]?fmt/\d+", _input) != None:
            result = PuidSearchResult.search_puid( _input, lang = APP.config[ConfKey.WIKIBASE_LANGUAGE])
            for res in result:
                item = DF.qid_to_basic_details(res.format)
                options = [[res.format, res.label, item['description']]]
                # load other options in case user was not searching by PUID
                options += [[ x['id'], x['label'], x['description']] for x in DF.search_result_list(_input)]
                previewItem = DF.item_detail_parse(res.format)
                return render_template('preview-item.html', selected=previewItem, options=options)
    except Exception as e:
        logging.exception("Error Searching for PUID: %s", str(e))
    options = DF.search_result_list(_input)
    return render_template('search_results.html', options=options)

@APP.route("/preview", methods=['POST'])
def process_preview_page():
    """Show a preview of a selected search result."""
    return redirect('/'+request.form['qid']+'?options='+request.form['optionList'])

@APP.route("/q<id>")
@APP.route("/Q<id>")
def selected_item(id):
    """If the item ID is already known, the user can enter in the url"""
    qid = 'Q'+id
    preview_item = DF.item_detail_parse(qid)
    options = request.args.get('options', default = 0, type = str)
    if type(options) is str:
        options = json.loads(options)
    else:
        basic_details = DF.qid_to_basic_details(qid)
        options = [[qid, basic_details['label'], basic_details['description']]]
    return render_template('preview-item.html', selected=preview_item, options=options, page='preview')

@APP.route("/contribute", methods=['POST'])
def process_contribute_url():
    """Processes contribute page into a state-saving url."""
    return redirect('/contribute?qid='+request.form['qid']+'&options='+request.form['optionList'])

@APP.route("/contribute")
def contribute_selected_page():
    """Handles a user's contributed statements."""
    qid = request.args.get('qid', type = str)
    preview_item = DF.item_detail_parse(qid)
    options = request.args.get('options', default = 0, type = str)
    if type(options) is str:
        options = json.loads(options)
    else:
        basic_details = DF.qid_to_basic_details(qid)
        options = [[qid, basic_details['label'], basic_details['description']]]
    return render_template('contribute.html', selected=preview_item, options=options, page='contribute')


@APP.route("/api-load-item", methods=['POST'])
def api_load_item():
    """Routing after the user searches an item in a form"""
    logging.debug("Processing user POST request.")
    qid = request.form['qid']
    if qid in [None, ""]:
        qid = "None"
        return "error, item not found"
    output = DF.item_detail_parse(qid)
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
    logging.debug("Running Flask App")
    APP.run(host='0.0.0.0')
