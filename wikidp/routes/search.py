#!/usr/bin/python
# coding=UTF-8
#
# WikiDP Wikidata Portal
# Copyright (C) 2020
# All rights reserved.
#
# This code is distributed under the terms of the GNU General Public
# License, Version 3. See the text file "COPYING" for further details
# about the terms of this license.
#
# This is a python __init__ script to create the app and import the
# main package contents
"""Module to handle web page search functions."""
from flask import redirect, render_template, request
from wikidp.config import APP
from wikidp.controllers import search as search_controller


@APP.route("/search", methods=['POST'])
def route_process_site_search():
    """
    Process a search request into a state-saving url.

    Returns (Response):

    """
    query = request.form['userInput'].strip()
    return redirect(f'/search?q={query}')


@APP.route("/search")
def route_site_search():
    """
    Display the most likely results of a users search.

    Notes:
        if only one result returned,
        then user is automatic redirected to preview that item.

    Returns (Response):

    """
    search_string = request.args.get('q', default='', type=str)
    context = search_controller.get_search_result_context(search_string)
    if len(context) == 1:
        return redirect(f'/{context[0]["qid"]}')
    return render_template('search_results.html', options=context)


@APP.route("/search/puid/<string:puid>")
def route_search_by_puid(puid):
    """Display a list of extensions and media types."""
    new_puid, results = search_controller.get_search_by_puid_context(puid)
    return render_template('puid_results.html', results=results, puid=new_puid)
