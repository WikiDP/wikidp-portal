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
# This is a python __init__ script to create the app and import the
# main package contents
""" Module for application form routes. """
from flask import (
    redirect,
    request,
)
from wikidp.config import APP


@APP.route("/preview", methods=['POST'])
def route_form_preview_item():
    """Show a preview of a selected search result."""
    return redirect('/'+request.form['qid']+'/preview'+'?options='+request.form['optionList'])


@APP.route("/contribute", methods=['POST'])
def route_form_contribute_item():
    """Processes contribute page into a state-saving url."""
    qid = request.form['qid']
    return redirect('/{qid}/contribute?qid={qid}&options={opts}'. \
        format(qid=qid, opts=request.form['optionList']))
