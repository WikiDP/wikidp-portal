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
from flask import request

from wikidp.controllers.api import get_property_checklist_from_schema
from wikidp.utils import (
    get_directory_filenames_with_subdirectories,
    get_item_property_counts,
    item_detail_parse,
)

SCHEMA_DIRECTORY_PATH = 'wikidp/schemas/'


def get_item_context(qid, with_claims=True):
    """
    Retrieve an item by QID with accompanying claims if requested.

    Args:
        qid (str):
        with_claims (bool):

    Returns (Tuple[dict, Optional[list], Optional[list]]):

    """
    selected_item = item_detail_parse(qid, with_claims=with_claims)
    options = None
    schemas = None
    if selected_item:
        _options = request.args.get('options', default=None, type=str)
        options = _options.split(',') if _options else [qid]
        schemas = get_schema_list()
    return selected_item, options, schemas


def get_checklist_context(qid, schema):
    """
    Create a property checklist render context from a schema.

    Args:
        qid (str):
        schema (str):

    Returns (List[Dict]):

    """
    checklist = get_property_checklist_from_schema(schema)
    if checklist:
        counts = get_item_property_counts(qid)
        output = [{
            "id": prop['id'],
            "label": prop['propertyLabel'],
            "description": prop['propertyDescription'],
            "type": prop["value_type"],
            "count": counts.get(prop['id'], 0),
            "qualifiers": prop["qualifiers"],
        } for prop in checklist]
        return output
    return []


def get_schema_list():
    """Get a flat list of schema files."""
    return get_directory_filenames_with_subdirectories(SCHEMA_DIRECTORY_PATH)
