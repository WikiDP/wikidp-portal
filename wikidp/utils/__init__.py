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
# This is a python __init__ script to create the app and import the
# main package contents
"""Package description file for utils and general purpose WikiDP utilities."""
from collections import namedtuple
from datetime import datetime
import json
import logging
from os import listdir
from os.path import (
    isfile,
    join,
    splitext,
)
import re
from string import Template
from urllib import request as urllib_request

import validators

from wikidp.const import (
    ITEM_REGEX,
    PROPERTY_REGEX,
    LANG,
    FALLBACK_LANG,
)
from wikidp.sparql import (
    ALL_LANGUAGES_QUERY,
    ALL_QUALIFIER_PROPERTIES,
    PROPERTY_ALLOWED_QUALIFIERS,
    PROPERTY_QUERY,
)

from . import (
    wd_int_utils,
)

def dedupe_by_key(dict_list, key):
    """
    Remove duplicates from a list based on matching key's value.

    Args:
        dict_list (List[Dict]):
        key (str):

    Returns (List[Dict]):
    """

    output = []
    found_values = set()
    for item in dict_list:
        value = item.get(key)
        if value not in found_values:
            output.append(item)
            found_values.add(value)
    return output


def _flatten_string(_string):
    return " ".join(_string.split())


def _file_to_label(filename):
    output = _remove_extension_from_filename(filename)
    return output.replace('_', ' ').title()


def get_pid_from_string(input_string):
    """Parse and return a property id from a string value."""
    regex_search = re.search(PROPERTY_REGEX, input_string)
    return regex_search.group() if regex_search else False


def get_qid_from_string(input_string):
    """Parse and return an item id from a string value."""
    regex_search = re.search(ITEM_REGEX, input_string)
    return regex_search.group() if regex_search else False

def _entity_id_to_int(entity):
    return int(entity[1:])

def get_property(pid):
    """Return the first value from a list of properties."""
    prop_response = get_property_details_by_pid_list([pid])
    return prop_response[0] if prop_response else None

def convert_list_to_value_string(lst):
    """
        Convert a list of values to a string.

        Arg: lst, ex: ['P31', 'P5', 'P123']
        Returns: "(wd:P31)(wd:P5)(wd:P123)"
    """
    return '(wd:{0})'.format(')(wd:'.join(map(str, lst)))

def get_all_languages():
    """
    Get list of all Wikimedia languages from Wikidata.

    Returns (List[Dict[str, str]]):

    Examples:
        [
            . . . ,

            {
                'item': 'http://www.wikidata.org/entity/Q845441',
                'code': 'sdc',
                'itemLabel': 'Sassarese',
                'label': 'Sassarese',
                'display': '{{#language:sdc}}'
            }
            . . . ,
        ]

    """
    query = _flatten_string(ALL_LANGUAGES_QUERY)
    return wd_int_utils.process_query_string(query)


def get_all_qualifier_properties():
    """Return all of the qualifiers for a particular property."""
    query = _flatten_string(ALL_QUALIFIER_PROPERTIES)
    return wd_int_utils.process_query_string(query)


def get_allowed_qualifiers_by_pid(pid):
    """Return all legal quailifiers for a partiular property."""
    value = convert_list_to_value_string([pid])
    query = PROPERTY_ALLOWED_QUALIFIERS_TEMPLATE.substitute(values=value)
    return wd_int_utils.process_query_string(query)

def get_property_details_by_pid_list(pid_list):
    """Return property details from a property id list."""
    values = convert_list_to_value_string(pid_list)
    query = PROPERTY_QUERY_TEMPLATE.substitute(values=values)
    return wd_int_utils.process_query_string(query)

def get_directory_filenames_with_subdirectories(directory_path):
    """Returns a a dictionary of filenames from a directory hierarchy."""
    output = []
    for item in listdir(directory_path):
        i = {'name': item, 'label': _file_to_label(item)}
        this_path = join(directory_path, item)
        if isfile(this_path):
            i['type'] = 'file'
        else:
            i['type'] = 'directory'
            i['files'] = get_directory_filenames_with_subdirectories(this_path)
        output.append(i)
    return output


def _remove_extension_from_filename(filename_string):
    return splitext(filename_string)[0]


def time_formatter(time):
    """Convert wikidata's time json to a human readable string."""
    try:
        formatted_time = datetime.strptime(time, '+%Y-%m-%dT%H:%M:%SZ')
        return formatted_time.strftime("%A, %B %-d, %Y")
    except (ValueError, TypeError):
        return time


def get_wikimedia_image_url_from_title(title):
    """Convert image title to the url location of that file it describes."""
    # TO DO: Url's do not work with non-ascii characters
    #    For example, the title of the image for Q267193 [Sublime Text]
    #    is "Скриншот sublime text 2.png"
    title = title.replace(" ", "_")
    url = ("https://commons.wikimedia.org/w/api.php?action=query&prop"
           "=imageinfo&iiprop=url&titles=File:{}&format=json").format(title)
    try:
        url = urllib_request.urlopen(url)
        base = json.loads(url.read().decode())["query"]["pages"]
        # Return just the first item
        for item in base:
            return base[item]["imageinfo"][0]["url"]
        return "https://commons.wikimedia.org/wiki/File:"+title
    except (UnicodeEncodeError, KeyError):
        return "https://commons.wikimedia.org/wiki/File:"+title


def parse_wd_response_by_key(item, key, default=None):
    """
    Parse WikiData Response dictionary into a python list of values.

    Args:
        item (dict): Returned output of using wikidataintegrator's wd_json_representation
        key (str): Desired key to extract values of from item
        default (optional): Expected return if value does not exist for fallback language

    Returns ([str]): list of values
    """
    value_dict = item.get(key)
    if value_dict:
        values = get_lang(value_dict, default=default)
        if isinstance(values, list):
            return [x.get('value') for x in values]
        if isinstance(values, dict):
            return values.get('value', values)
        return values
    return default


def get_lang(_dict, default=None):
    """
    Get language value of a dictionary, fallback language if not available.

    Args:
        _dict (dict): Dictionary for getting value
        default (optional): Expected return if value does not exist for fallback language

    Returns: value of dictionary's language key or default
    """
    if not _dict:
        pass
    value = _dict.get(LANG)
    if value:
        return value
    return _dict.get(FALLBACK_LANG, default)


# pylint: disable=R0914
def item_detail_parse(qid, with_claims=True):
    """
    Use the JSON representation of wikidataintegrator to parse the item ID specified.

    Returns a new dictionary of previewing information and a dictionary of property counts.
    """
    item = wd_int_utils.get_item_json(qid)
    if not item:
        return False
    label = parse_wd_response_by_key(item, 'labels', default="Item {}".format(qid))
    aliases = parse_wd_response_by_key(item, 'aliases', default=[])
    description = parse_wd_response_by_key(item, 'descriptions', default='')
    output_dict = {'qid': qid, 'label': label, 'aliases': aliases, 'description': description}
    if with_claims:
        claim_list = []
        ex_list = []
        categories = []
        claims = get_claims_from_json(item)
        for pid, claim_dict in sorted(claims.items(), key=lambda x: _entity_id_to_int(x[0])):
            value_list = []
            add_to_ex_list = False
            for json_details in claim_dict:
                val = parse_snak(pid, json_details.get('mainsnak'))
                if val:
                    val['references'] = _parse_references(json_details)
                    val['qualifiers'] = _parse_qualifiers(json_details)
                    value_list.append(val)
                    if val.get('parse_type') == 'external-id':
                        add_to_ex_list = True
                    # Determining the 'category' of the item
                    # from the 'instance of' and 'subclass of' properties
                    elif pid in ['P31', 'P279']:
                        categories.append(val)
            parsed_claim = {'pid': pid, 'values': value_list}
            # pylint: disable=W0106
            ex_list.append(parsed_claim) if add_to_ex_list else claim_list.append(parsed_claim)
        output_dict['external_links'] = ex_list
        output_dict['claims'] = claim_list
        output_dict['categories'] = categories
    return output_dict


def _parse_qualifiers(json_details):
    qualifier_set = json_details.get('qualifiers')
    return _parse_snak_set(qualifier_set)


def _parse_references(json_details):
    reference_list = json_details.get('references')
    if reference_list:
        reference_set = reference_list[0].get('snaks')
        return _parse_snak_set(reference_set)
    return []


def _parse_snak_set(snak_set):
    parsed_snaks = []
    if snak_set:
        for pid, snak_list in snak_set.items():
            values = []
            for snak in snak_list:
                val = parse_snak(pid, snak)
                if val:
                    values.append(val)
            if values:
                parsed_snaks.append({'pid': pid, 'values': values})
    return parsed_snaks

def get_item_property_counts(qid):
    """
    Count the number of values in a claim by property.

    Args:
        qid (str): Wikidata Identifier, ex: "Q1234"

    Returns:
        Dict: {k(str): v(int)} where k is Wikidata Property identifier string and v is count
    """
    selected_item = wd_int_utils.get_item_json(qid)
    claims = get_claims_from_json(selected_item)
    counts = {}
    for pid, values in claims.items():
        counts[pid] = len(values)
    return counts


def get_claims_from_json(item_json):
    """
    Get claim dictionary from WD Item Json Representation.

    Args:
        item_json (dict): Returned value of WDItemEngine().wd_json_representation

    Returns:
        Dictionary of {k:v} where k is property id and v is list of value dictionaries
    """
    return item_json.get('claims', {})


# pylint: disable=R0912
def parse_snak(pid, snak):
    """Use a claim's json_details and output the parsed data into the output_dict."""
    try:
        if snak['snaktype'] == 'novalue' or 'datavalue' not in snak:
            return None
        #  Parsing the statements & values by data type
        parse_type = snak.get('datatype')
        data_type = snak['datavalue'].get('type')
        data_value = snak['datavalue'].get('value')

        #  In the event the value is an image file name, convert the title to the image's url
        if pid in ["P18", "P154"]:
            val = get_wikimedia_image_url_from_title(data_value)
            parse_type = 'image'
        elif parse_type == 'external-id':
            val = {'url': format_url_from_property(pid, data_value), 'label': data_value}
        elif data_type == 'string':
            val = data_value
            if validators.url(val):
                parse_type = 'url'
        elif data_type == 'wikibase-entityid':
            parse_type = data_value.get('entity-type')
            if parse_type == 'property':
                val = 'P{}'.format(data_value.get('numeric-id'))
            else:
                val = data_value.get('id')
        elif data_type == 'time':
            val = time_formatter(data_value.get('time'))
            parse_type = 'time'
        elif data_type == 'quantity' and 'amount' in data_value:
            num = data_value.get('amount')
            try:
                val = int(num)
            except ValueError:
                val = float(num)
        elif data_type == 'monolingualtext':
            val = '"{}" (language: {})'.format(data_value.get('text', ''),
                                               data_value.get('language', 'unknown'))
        else:
            val = "Unable To Parse Value {}".format(data_type)
        return {'value': val, 'parse_type': parse_type, 'type': data_type}
    except KeyError:
        logging.exception("Unexpected exception parsing claims.")
        return None


def format_url_from_property(pid, value):
    """
    Input property identifier (P###) for a given url type.

    Looks up that wikidata property id's url format (P1630) and creates a url
    with the value using the format.
    """
    value = value.strip()
    prop = get_property(pid)
    if 'formatter_url' in prop:
        return prop.get("formatter_url").replace("$1", value)
    return None

def _create_query_template(_string):
    flat_str = _flatten_string(_string)
    return Template(flat_str)

# Register Template Queries Here
PROPERTY_QUERY_TEMPLATE = _create_query_template(PROPERTY_QUERY)
PROPERTY_ALLOWED_QUALIFIERS_TEMPLATE = _create_query_template(PROPERTY_ALLOWED_QUALIFIERS)
