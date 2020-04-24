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
from wikidataintegrator.wdi_core import (
    WDItemEngine,
    WDItemID,
    WDString,
)
from wikidataintegrator.wdi_login import WDLogin

from config import APP
from const import ConfKey
from models import FileFormat
from utils import (
    get_pid_from_string,
    get_property_details_by_pid_list,
)

# TODO: Account for all dataTypes
STRING_TO_WD_DATATYPE = {
    "WikibaseItem": WDItemID,
    "String": WDString,
}
MEDIAWIKI_API_URL = APP.config[ConfKey.MEDIAWIKI_API_URL]
SCHEMA_DIRECTORY_PATH = 'wikidp/schemas/'
# TODO: Set this up as environment variable
# TEMP_LOGIN = WDLogin(mediawiki_api_url=MEDIAWIKI_API_URL)
TEMP_LOGIN = WDLogin


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
                props.extend(exp['predicate'] for exp in expression_list
                             if 'predicate' in exp)
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
    return []


def write_claims_to_item(qid):
    logging.debug("Processing user POST request.")
    # TODO: Pass this in this dictionary
    json_data_claims = request.get_json()
    # Build statements
    data = [
        build_statement(json_data.get('pid'), json_data.get('value'),
                        json_data.get('type'), json_data.get('qualifiers'))
        for json_data in json_data_claims
    ]
    # Get wikidata item
    item = WDItemEngine(wd_item_id=qid, mediawiki_api_url=MEDIAWIKI_API_URL,
                        data=data)
    # Build login and Write to wikidata
    qid = item.write(TEMP_LOGIN)

    return jsonify({
        "message": f"Successfully Contributed {len(data)} "
                   f"Statements to Wikidata Item '{item.get_label()}' ({qid}).",
        "status": "success"
    })


def build_statement(prop, value, data_type, qualifier_data, reference_data):
    """Build Statement to Write to Wikidata.
    Args:
        prop (str): Wikidata Property Identifier [ex. 'P1234']
        value (str): Value matching accepted property
        data_type (str):
        qualifier_data (List[Dict]): list of data about qualifiers
        reference_data (List[Dict]): list of data about references
    Returns (WDBaseDataType):
    """

    qualifiers = [
        wd_datatype(qualifier.get('type'), value=qualifier.get('value'),
                    prop_nr=qualifier.get("pid"), is_qualifier=True)
        for qualifier in qualifier_data
    ]
    # The double list here is intentional based on the way Wikidataintegrator
    # expects the data type
    references = [[
        wd_datatype(reference.get('type'), value=reference.get('value'),
                    prop_nr=reference.get("pid"), is_reference=True)
        for reference in reference_data
    ]]

    return wd_datatype(data_type, prop_nr=prop, value=value,
                       qualifiers=qualifiers, references=references)


def wd_datatype(data_type_string, *args, **kwargs):
    """
    Create a WikidataIntegrator WDBaseDataType instance by a string name.

    Args:
        data_type_string (str):

    Returns (WDBaseDataType):

    """
    wd_datatype_class = STRING_TO_WD_DATATYPE[data_type_string]
    assert wd_datatype_class, f"Invalid Datatype '{wd_datatype_class}'"
    return wd_datatype_class(*args, **kwargs)


def get_all_file_formats():
    formats = FileFormat.list_formats()
    return formats
