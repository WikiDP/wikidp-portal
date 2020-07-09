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
"""Module for WikiDP pages."""
from flask import (
    json,
    request,
)

from wikidp.controllers.api import get_property_checklist_from_schema
from wikidp.utils import (
    item_detail_parse,
    get_directory_filenames_with_subdirectories,
    get_item_property_counts,
)

SCHEMA_DIRECTORY_PATH = 'wikidp/schemas/'


def get_item_context(qid, with_claims=True):
    """Retrieve an item by QID with accompaying claims if requested."""
    selected_item = item_detail_parse(qid, with_claims=with_claims)
    options = None
    schemas = None
    if selected_item:
        options = request.args.get('options', default=0, type=str)
        if isinstance(options, str):
            options = json.loads(options)
        else:
            options = [[qid, selected_item.get('label'), selected_item.get('description')]]
        schemas = get_schema_list()
    return selected_item, options, schemas


def get_checklist_context(qid, schema):
    """Create a property checklist from a schema."""
    checklist = get_property_checklist_from_schema(schema)
    if checklist:
        counts = get_item_property_counts(qid)
        output = [{
            "id": prop['id'],
            "label": prop['propertyLabel'],
            "description": prop['propertyDescription'],
            "type": prop["value_type"],
            "count": counts.get(prop['id'], 0)
            } for prop in checklist]
        return output
    return []


def get_schema_list():
    """Get a flat list of schema files."""
    return get_directory_filenames_with_subdirectories(SCHEMA_DIRECTORY_PATH)
