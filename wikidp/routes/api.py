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
"""Flask application api routes for Wikidata portal."""
import logging

from flask import (
    jsonify,
    request,
)

from wikidp.config import APP
from wikidp.controllers.api import (
    get_all_file_formats,
    get_property_checklist_from_schema,
    write_claims_to_item,
)
from wikidp.controllers.auth import get_wdi_login
from wikidp.controllers.search import search_result_list
from wikidp.utils import (
    get_all_languages,
    get_all_qualifier_properties,
    get_allowed_qualifiers_by_pid,
    get_property,
    item_detail_parse,
)


@APP.route("/api/")
def route_api_welcome():
    """Landing Page API index."""
    return 'Welcome to the WikiDP API'


@APP.route("/api/<item:qid>", methods=['GET', 'POST'])
def route_api_get_item(qid):
    """User posts a item-id and returns json of (id, label, desc, aliases)."""
    item = item_detail_parse(qid, with_claims=True)
    return jsonify(item)


@APP.route("/api/<item:qid>/summary", methods=['GET', 'POST'])
def route_api_get_item_summary(qid):
    """User posts a item-id and returns json of (id, label, desc, aliases)."""
    item = item_detail_parse(qid, with_claims=False)
    return jsonify(item)


@APP.route("/api/items", methods=['GET', 'POST'])
def route_api_get_item_summary_list():
    """
    Get a list of Wikidata Item.

    Returns (Response): JSON list with id, label, description, and aliases

    """
    if request.method == 'GET':
        qids = request.args.get('qids').split(',')
    else:
        qids = request.get_json()
    items = [item_detail_parse(qid, with_claims=False) for qid in qids]
    return jsonify(items)


@APP.route("/api/<item:qid>/claims/write", methods=['POST'])
def route_api_write_claims_to_item(qid):
    """User posts a JSON object of claims to contribute to an item."""
    logging.debug("Processing user POST request.")
    wdi_login = get_wdi_login()
    assert wdi_login, "Must be Authenticated"
    json_data = request.get_json()
    return write_claims_to_item(qid, json_data, wdi_login)


@APP.route("/api/<prop:pid>", methods=['GET', 'POST'])
def route_api_get_property(pid):
    """Return JSON representation of a property by PID."""
    prop = get_property(pid)
    return jsonify(prop)


@APP.route("/api/<prop:pid>/qualifiers", methods=['GET', 'POST'])
def route_api_get_allowed_qualifiers_by_pid(pid):
    """Return JSON representation of allowed property qualifiers by PID."""
    output = get_allowed_qualifiers_by_pid(pid)
    return jsonify(output)


@APP.route("/api/property/qualifiers", methods=['GET', 'POST'])
def route_api_get_all_qualifier_properties():
    """Return JSON representation of all property qualifiers."""
    output = get_all_qualifier_properties()
    return jsonify(output)


@APP.route("/api/language/", methods=['GET', 'POST'])
def route_api_get_all_languages():
    """Return JSON representation of all supported languages."""
    output = get_all_languages()
    return jsonify(output)


@APP.route("/api/search/<search_string>", methods=['GET', 'POST'])
def route_api_search_item_by_string(search_string):
    """Post string, returns list of json of (id, label, desc, aliases)."""
    _string = search_string.strip()
    output = search_result_list(_string)
    return jsonify(output)


@APP.route("/api/schema/<path:schema_name>/properties")
def route_api_get_properties_by_schema(schema_name):
    """Return a JSON representation of properties from a particular schema."""
    prop_list = get_property_checklist_from_schema(schema_name)
    return jsonify(prop_list)


@APP.route("/api/browse/file_format", methods=['GET', 'POST'])
def route_api_browse_file_format():
    """Return a JSON representation of a list of all file formats."""
    format_list = get_all_file_formats()
    return jsonify([x.api_dict() for x in format_list])
