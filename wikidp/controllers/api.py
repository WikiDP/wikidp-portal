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

from flask import (
     json,
     jsonify,
     request,
)
import pywikibot

from wikidp.utils import (
    get_pid_from_string,
    get_property_details_by_pid_list,
)


SANDBOX_API_URL = 'https://test.wikidata.org/w/'
SANDBOX_SPARQL_URL = 'https://test.wikidata.org/proxy/wdqs/bigdata/namespace/wdq/'
SITE = pywikibot.Site("test", "wikidata")
REPO = SITE.data_repository()
SCHEMA_DIRECTORY_PATH = 'wikidp/schemas/'


def load_schema(schema_name):
    try:
        with open(SCHEMA_DIRECTORY_PATH+schema_name) as data_file:
            return json.load(data_file)
    except (Exception, FileNotFoundError):
        return False


def get_schema_properties(schema_name):
    data = load_schema(schema_name)
    if data is False:
        return False
    props = []
    for shape in data.get('shapes', []):
        shape_expression = shape.get('expression')
        if shape_expression:
            expression_list = shape_expression.get('expressions')
            if expression_list:
                props.extend(exp.get('predicate') for exp in expression_list if 'predicate' in exp)
            predicate = shape_expression.get('predicate')
            if predicate:
                props.append(predicate)
    output = []
    for prop in props:
        pid = get_pid_from_string(prop)
        if pid and pid not in output:
            output.append(pid)
    return output


def get_property_checklist_from_schema(schema_name):
    pid_list = get_schema_properties(schema_name)
    if pid_list:
        return get_property_details_by_pid_list(pid_list)
    else:
        output = []
    return output


def write_claims_to_item(qid):
    logging.debug("Processing user POST request.")
    user_claims = request.get_json()
    successful_claims = []
    failure_claims = []
    logging.debug("Writing Claim to Q175461 as a mock for writing Claims to: "+qid)
    item = pywikibot.ItemPage(REPO, u"Q175461")  # WIKIDATA TESTING ITEM
    # item = pywikibot.ItemPage(REPO, qid)
    for user_claim in user_claims:
        write_status = write_claim(item, user_claim['pid'], user_claim['value'], user_claim['type'])
        if write_status is True:
            successful_claims.append(user_claim)
        else:
            failure_claims.append(user_claim)
    output = {'status': 'success', 'successful_claims': successful_claims, 'failure_claims': failure_claims}
    return jsonify(output)


def write_claim(item, prop_string, value, data_type, meta=False):
    """Write a claim to WikiData.

    Args:
        item (pywikibot.ItemPage): Wikidata Item Model
        prop_string (str): Wikidata Property Identifier [ex. 'P1234']
        value (str): Value matching accepted property
        data_type: (could be other data types)
        meta (dict, optional): Contains information about qualifiers/references/summaries
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # TODO: Account for all dataTypes
        claim = pywikibot.Claim(REPO, prop_string)
        if data_type == 'WikibaseItem':
            target = pywikibot.ItemPage(REPO, value)
        # elif data_type == 'Coordinate'
        # elif data_type == 'String'
        else:
            target = value
        claim.setTarget(target)
        if meta:
            # TODO: Add Ability to include references, summaries, and qualifiers
            pass
        item.addClaim(claim, summary=u'Adding claim')
        return True
    except (TypeError, Exception):
        return False
