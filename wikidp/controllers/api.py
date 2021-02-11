#!/usr/bin/python
# coding=UTF-8
#
# WikiDP Wikidata Portal
# Copyright (C) 2021
# All rights reserved.
#
# This code is distributed under the terms of the GNU General Public
# License, Version 3. See the text file "COPYING" for further details
# about the terms of this license.
#
"""Flask application routes for Wikidata portal."""
from collections import defaultdict
from flask import (
    json,
    jsonify,
)
from wikidataintegrator.wdi_core import (
    WDExternalID,
    WDItemEngine,
    WDItemID,
    WDMonolingualText,
    WDString,
    WDQuantity,
    WDTime,
    WDUrl,
)

from wikidp.config import APP
from wikidp.const import ConfKey
from wikidp.models import FileFormat
from wikidp.utils import (
    get_pid_from_string,
    get_property_details_by_pid_list,
)
from wikidp.utils.wd_int_utils import format_date

WD_DATATYPE_MAP = {
    "ExternalId": WDExternalID,
    "Monolingualtext": WDMonolingualText,
    "Quantity": WDQuantity,
    "String": WDString,
    "Time": WDTime,
    "Url": WDUrl,
    "WikibaseItem": WDItemID,
}
MEDIAWIKI_API_URL = APP.config[ConfKey.MEDIAWIKI_API_URL]
SCHEMA_DIRECTORY_PATH = 'wikidp/schemas/'


def load_schema(schema_name):
    """Load a schema file by name."""
    try:
        with open(SCHEMA_DIRECTORY_PATH+schema_name) as data_file:
            return json.load(data_file)
    except FileNotFoundError:
        return None


def parse_predicate(expression):
    """
    Get the Property Id from an expression's predicate.

    Args:
        expression (Dict):

    Returns (Tuple[Optional[str], bool]):

    """
    predicate = expression.get("predicate", "")
    pid = get_pid_from_string(predicate)
    if pid:
        return pid, "qualifier" in predicate
    return None, False


def parse_expressions(schema):
    """
    Parse Shape Expressions of a Schema.

    Args:
        schema (Dict):

    Returns (defaultdict[str, set]):

    """
    prop_map = defaultdict(set)
    for shape in schema.get('shapes', []):
        outer_expression = shape.get('expression', {})
        props = set()
        qualifiers = set()
        for expression in outer_expression.get('expressions', []):
            pid, is_qualifier = parse_predicate(expression)
            if pid and is_qualifier:
                qualifiers.add(pid)
            elif pid:
                props.add(pid)
            for inner_expression in expression.get('expressions', []):
                pid, _ = parse_predicate(inner_expression)
                if pid:
                    prop_map[pid] = prop_map[pid]
        for prop in props:
            prop_map[prop].update(qualifiers)
    return prop_map


def get_schema_properties(schema_name):
    """
    Get property constraints of a particular schema.

    Args:
        schema_name (str): Relative file name of schema.

    Examples:
        >>> get_schema_properties('file_format_id_pattern')
        { "P31": {"P123"}, "P279": {}, ... }

    Returns (Optional[defaultdict[str, set]]):

    """
    data = load_schema(schema_name)
    if not data:
        return None
    return parse_expressions(data)


def flatten_prop_map(prop_map):
    """
    Extract all Ids from a property map.

    Args:
        prop_map (defaultdict[str, set]):

    Returns:

    """
    prop_ids = set()
    for prop, qualifiers in prop_map.items():
        prop_ids.add(prop)
        prop_ids.update(qualifiers)
    return prop_ids


def get_property_checklist_from_schema(schema_name):
    """
    Create a property checklist from a schema.

    Args:
        schema_name (str):

    Returns (List[Dict]):

    """
    prop_map = get_schema_properties(schema_name)
    if not prop_map:
        return []
    all_prop_ids = flatten_prop_map(prop_map)
    all_prop_data = {
        prop.get("id"): prop
        for prop in get_property_details_by_pid_list(all_prop_ids)
    }
    checklist = []
    for pid, qualifiers in prop_map.items():
        data = all_prop_data[pid]
        data["qualifiers"] = [
            all_prop_data[qualifier]
            for qualifier in qualifiers
        ]
        checklist.append(data)
    return checklist


def write_claims_to_item(qid, json_data, wdi_login):
    """
    Write new claims to an item.

    Args:
        qid (str): Wikidata Identifier
        json_data (List[Dict]): Data from request
        wdi_login (WDLogin):

    Returns (Response):

    """
    # Build statements
    data = [
        build_statement(claim_data.get('pid'), claim_data.get('value'),
                        claim_data.get('type'), claim_data.get('qualifiers'),
                        claim_data.get('references'))
        for claim_data in json_data
    ]
    props = [statement.prop_nr for statement in data]
    # Get wikidata item
    item = WDItemEngine(wd_item_id=qid, mediawiki_api_url=MEDIAWIKI_API_URL,
                        data=data, append_value=props)
    qid = item.write(wdi_login)
    return jsonify({
        "message": f"Successfully Contributed {len(data)} "
                   f"Statements to Wikidata Item '{item.get_label()}' ({qid}).",
        "status": "success"
    })


def build_statement(prop, value, data_type, qualifier_data, reference_data):
    """
    Build Statement to Write to Wikidata.

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
    ] if qualifier_data else None
    # The double list here is intentional based on the way Wikidataintegrator
    # expects the data type
    references = [[
        wd_datatype(reference.get('type'), value=reference.get('value'),
                    prop_nr=reference.get("pid"), is_reference=True)
        for reference in reference_data
    ]] if reference_data else None

    return wd_datatype(data_type, prop_nr=prop, value=value,
                       qualifiers=qualifiers, references=references)


def wd_datatype(data_type, value, *args, **kwargs):
    """
    Create a WikidataIntegrator WDBaseDataType instance by a string name.

    Args:
        data_type (str):
        value (str):

    Returns (WDBaseDataType):

    """
    wd_datatype_class = WD_DATATYPE_MAP[data_type]
    assert wd_datatype_class, f"Invalid Datatype '{wd_datatype_class}'"
    if issubclass(wd_datatype_class, WDTime):
        time = format_date(value)
        return wd_datatype_class(time=time, *args, **kwargs)
    return wd_datatype_class(value=value, *args, **kwargs)


def get_all_file_formats():
    """
    Get all File Formats.

    Returns (List[FileFormat]):

    """
    formats = FileFormat.list_formats()
    return formats
