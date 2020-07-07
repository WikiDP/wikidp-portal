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
"""Flask application routes for Wikidata portal."""
from flask import (
    json,
    jsonify,
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
WIKIDATA_PASSWORD = APP.config[ConfKey.WIKIDATA_PASSWORD]
WIKIDATA_USER_NAME = APP.config[ConfKey.WIKIDATA_USER_NAME]
SCHEMA_DIRECTORY_PATH = 'wikidp/schemas/'


def build_login():
    """
    Build a WDI Login.

    Notes:
        TODO: Add params to use OAuth token once configured
        This is a temporary function to stub where we can thread
        OAuth through this entry-point when it is configured.
        Currently, it uses system-wide user/pwd credentials to login just
        to demonstrate writing behavior.

    Returns (WDLogin):

    """
    return WDLogin(mediawiki_api_url=MEDIAWIKI_API_URL,
                   user=WIKIDATA_USER_NAME,
                   pwd=WIKIDATA_PASSWORD)


def load_schema(schema_name):
    """Load a schema file by name."""
    try:
        with open(SCHEMA_DIRECTORY_PATH+schema_name) as data_file:
            return json.load(data_file)
    except FileNotFoundError:
        return False


def get_schema_properties(schema_name):
    """Get all of the properties of a particular schema."""
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
    """Create a property checklist from a schema."""
    pid_list = get_schema_properties(schema_name)
    if pid_list:
        return get_property_details_by_pid_list(pid_list)
    return []


def write_claims_to_item(qid, json_data):
    """
    Write new claims to an item.

    Args:
        qid (str): Wikidata Identifier
        json_data (List[Dict]): Data from request
    """

    # Build statements
    data = [
        build_statement(claim_data.get('pid'), claim_data.get('value'),
                        claim_data.get('type'), claim_data.get('qualifiers'),
                        claim_data.get('references'))
        for claim_data in json_data
    ]
    # Get wikidata item
    item = WDItemEngine(wd_item_id=qid, mediawiki_api_url=MEDIAWIKI_API_URL,
                        data=data)
    # Build login and Write to wikidata
    # TODO: Add params to use request OAuth token from request once configured
    wd_login = build_login()
    qid = item.write(wd_login)

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
