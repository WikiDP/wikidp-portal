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
""" Flask application api routes for Wikidata portal. """
from wikidp import APP
from wikidp.controllers import api as api_controller

@APP.route("/api/")
def route_api_welcome():
    """Landing Page API index"""
    return 'Welcome to the WikiDP API'

@APP.route("/api/search/<search_string>", methods=['GET','POST'])
def route_api_search_item_by_string(search_string):
    """User posts a string and returns list of json of (id, label, description, aliases)"""
    return api_controller.search_item_by_string(search_string)

@APP.route("/api/<qid>/label", methods=['GET', 'POST'])
def route_api_get_item_label(qid):
    """User posts a item-id and returns json of (id, label, description, aliases)"""
    return api_controller.get_item_label(qid)

@APP.route("/api/schema/<path:schema_name>/properties")
def route_api_get_properties_by_schema(schema_name):
    return api_controller.get_property_checklist_from_schema(schema_name)


@APP.route("/api/<qid>/claims/write", methods=['POST'])
def route_api_write_claims_to_item(qid):
    """ User posts a JSON object of claims to contribute to an item"""
    return api_controller.write_claims_to_item(qid)
