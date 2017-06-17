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
from flask import request
from wikidp import APP
from wikidp.model import FileFormat
from wikidp.lists import Properties
import wikidp.DisplayFunctions as DF
# options = ["default", "options", "for testing"]
options = []
@APP.route("/")
def list_extensions():
    """Displays a list of extensions and media types."""
    formats = FileFormat.list_formats()
    return render_template('home.html', formats=formats)

@APP.route("/user")
def user_home(qid = False, stringSearch = True):
    """Main page for viewing, selecting, and updating items"""
    global options
    details = {}
    properties = Properties()
    if qid == False: 
    	qid = (None, None)
    	options = []
    elif stringSearch == False: 
    	details, counts = DF.item_detail_parse(qid)
    	qid = (qid, DF.qid_label(qid))
    # Possibly just an else (havent run through contingencies)
    elif (stringSearch == True) and (qid != False):
    	qid, options, details, counts = DF.search_result(qid)

    return render_template('user/home.html', qid = qid, options=options, properties=properties, details=details)

@APP.route("/user", methods=['POST'])
def user_home_searched():
    """Routing after the user searches an item in a form"""
    global options
    stringSearch = True
    if request.form['searchType'] == 'QID':
    	stringSearch = False
    qid = request.form['QID']
    if qid in [None, ""]: qid = "None"

    return user_home(qid, stringSearch)

@APP.route("/user/<qid>")
def selected_item(qid):
    """If the item ID is already known, the user can enter in the url"""
    qid = qid.strip()
	# print (qid)
    properties = Properties()
    return user_home(qid, stringSearch=False)
	# return render_template('user/home.html', qid = qid, options=options, properties=properties, details={})
    # do something with folder_name
 

if __name__ == "__main__":
    APP.run()
