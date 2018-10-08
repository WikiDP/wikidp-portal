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

from flask import render_template, request, json, redirect, jsonify
from wikidp import APP
from wikidp.const import ConfKey
from wikidp.model import FileFormat, PuidSearchResult
from wikidp.lists import properties
import wikidp.DisplayFunctions as DF
import pywikibot
SANDBOX_API_URL = 'https://test.wikidata.org/w/'
SANDBOX_SPARQL_URL = 'https://test.wikidata.org/proxy/wdqs/bigdata/namespace/wdq/'
SITE = pywikibot.Site("test", "wikidata")
REPO = SITE.data_repository()


def search_item_by_string(search_string):
    """User posts a string and returns list of json of (id, label, description, aliases)"""
    logging.debug("Processing user POST request.")
    string = search_string.strip()
    output = DF.search_result_list(string)
    return jsonify(output)

def get_item_label(qid):
    """User posts a item-id and returns json of (id, label, description, aliases)"""
    logging.debug("Processing user POST request.")
    output = DF.qid_to_basic_details(qid)
    return jsonify(output)

def write_claims_to_item(qid):
    logging.debug("Processing user POST request.")
    user_claims = request.get_json()
    successful_claims, failure_claims = [], []
    for user_claim in user_claims:
        write_status = write_claim(qid, user_claim['pid'], user_claim['value'])
        if write_status is True:
            successful_claims.append(user_claim)
        else:
            failure_claims.append(user_claim)
    output = {'status': 'success', 'successful_claims': successful_claims, 'failure_claims':failure_claims}
    return jsonify(output)

def write_claim(qid, property, value, meta=False):
    '''Function for writing a claim to WikiData

    Args:
        qid (str): Wikidata Item Identifier [ex. 'Q1234']
        property (str): Wikidata Property Identifier [ex. 'P1234']
        value (str): Value matching accepted property type (could be other datatypes)
        meta (dict, optional): Contains information about qualifiers/references/summaries
    Returns:
        bool: True if successful, False otherwise
    '''
    try:
        # TODO: Convert to writes to any item by uncommenting line 34
        item = pywikibot.ItemPage(REPO, u"Q175461") # WIKIDATA TESTING ITEM
        # item = pywikibot.ItemPage(REPO, qid)
        claim = pywikibot.Claim(REPO, property)
        target = pywikibot.ItemPage(REPO, value)
        claim.setTarget(target)
        item.addClaim(claim, summary=u'Adding claim')
        return True
    except Exception as e:
        return False
