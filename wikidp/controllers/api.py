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
from wikidp.controllers import wd_write
@APP.route("/api/")
def api_welcome():
    """Landing Page API index"""
    return 'Welcome to the WikiDP API'

@APP.route("/api/<qid>/claims/write", methods=['POST'])
def api_write_claims_to_item(qid):
    logging.debug("Processing user POST request.")
    user_claims = request.get_json()
    successful_claims, failure_claims = [], []
    for user_claim in user_claims:
        write_status = wd_write.write_claim(qid, user_claim['pid'], user_claim['value'])
        if write_status is True:
            successful_claims.append(user_claim)
        else:
            failure_claims.append(user_claim)
    output = {'status': 'success', 'successful_claims': successful_claims, 'failure_claims':failure_claims}
    return json.dumps(output)

# TODO: Add the rest of the api routes to this file instead of the main controller.py
