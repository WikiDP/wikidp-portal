from collections import OrderedDict
from datetime import datetime
import json
import logging
from os import listdir
from os.path import isfile, join, splitext
import re
from string import Template

from urllib import request as urllib_request
from wikidataintegrator.wdi_core import WDItemEngine

from wikidp.const import (
    ITEM_REGEX,
    PROPERTY_REGEX,
    LANG,
    FALLBACK_LANG,
)
from wikidp.sparql import PROPERTY_QUERY


def remove_duplicates_from_list(lst):
    return list(dict.fromkeys(lst))


def flatten_string(_string):
    return " ".join(_string.split())


def get_pid_from_string(input_string):
    regex_search = re.search(PROPERTY_REGEX, input_string)
    return regex_search.group() if regex_search else False


def get_qid_from_string(input_string):
    regex_search = re.search(ITEM_REGEX, input_string)
    return regex_search.group() if regex_search else False


def get_property(pid):
    prop_response = get_property_details_by_pid_list([pid])
    return prop_response[0] if prop_response else None


def convert_list_to_value_string(lst):
    """
        Arg: lst, ex: ['P31', 'P5', 'P123']
        Returns: "(wd:P31)(wd:P5)(wd:P123)"
    """
    return '(wd:{0})'.format(')(wd:'.join(map(str, lst)))


def get_property_details_by_pid_list(pid_list):
    values = convert_list_to_value_string(pid_list)
    query_string = PROPERTY_QUERY_TEMPLATE.substitute(values=values)
    result = WDItemEngine.execute_sparql_query(query_string)
    return result['results'].get('bindings')


def get_directory_filenames_with_subdirectories(directory_path):
    output = []
    for item in listdir(directory_path):
        if isfile(join(directory_path, item)):
            output.append(item)
        else:
            output.append([item, get_directory_filenames_with_subdirectories(join(directory_path, item))])
    return output


def remove_extension_from_filename(filename_string):
    return splitext(filename_string)[0]


def list_sorting_by_length(elem):
    """Auxiliary sorting key function at the list level"""
    return len(elem[0])


def dict_sorting_by_length(elem):
    """Auxiliary sorting key function at the dictionary level"""
    return len(elem[0][0])


def time_formatter(time):
    """Converts wikidata's time json to a human readable string"""
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
    url = "https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url&titles=File:{}&format=json"\
        .format(title)
    try:
        url = urllib_request.urlopen(url)
        base = json.loads(url.read().decode())["query"]["pages"]
        # Return just the first item
        for item in base:
            return base[item]["imageinfo"][0]["url"]
        return "https://commons.wikimedia.org/wiki/File:"+title
    except (UnicodeEncodeError, KeyError, Exception):
        return "https://commons.wikimedia.org/wiki/File:"+title


def parse_wd_response_by_key(item, key, default=None):
    """
    Parse WikiData Response dictionary into a python list of values
    Args:
        item (dict): Returned output of using wikidataintegrator's wd_json_representation
        key (str): Desired key to extract values of from item
        default (optional): Expected return if value does not exist for fallback language

    Returns ([str]): list of values
    """
    value_dict = item.get(key)
    if value_dict:
        values = get_lang(value_dict, default=default)
        if type(values) is list:
            return [x.get('value') for x in values]
        if type(values) is dict:
            return values.get('value', values)
        return values
    return default


def get_lang(_dict, default=None):
    """
    Get language value of a dictionary, fallback language if not available
    Args:
        _dict (dict): Dictionary for getting value
        default (optional): Expected return if value does not exist for fallback language

    Returns: value of dictionary's language key or default

    """
    if _dict is {}:
        pass
    value = _dict.get(LANG)
    if value:
        return value
    return _dict.get(FALLBACK_LANG, default)


def item_detail_parse(qid, with_claims=True):
    """Uses the JSON representation of wikidataintegrator to parse the item ID specified (qid)
    and returns a new dictionary of previewing information and a dictionary of property counts"""
    item = get_item_json(qid)
    if item:
        label = parse_wd_response_by_key(item, 'labels', default="Item {}".format(qid))
        aliases = parse_wd_response_by_key(item, 'aliases', default=[])
        description = parse_wd_response_by_key(item, 'descriptions', default='')
        output_dict = {'qid': qid, 'label': label, 'aliases': aliases, 'description': description}
        if with_claims:
            output_dict['claims'] = {}
            output_dict['refs'] = {}
            output_dict['properties'] = {}
            output_dict['ex-ids'] = {}
            output_dict['categories'] = []
            claims = get_claims_from_json(item)
            properties = get_property_details_by_pid_list(claims.keys())
            cached_property_labels = {prop['id']['value']: prop['propertyLabel']['value'] for prop in properties}
            for claim in claims:
                property_label = cached_property_labels[claim]
                for json_details in claims[claim]:
                    output_dict = parse_claims(claim, property_label, json_details, output_dict,
                                               cached_property_labels)
            output_dict['claims'] = OrderedDict(sorted(output_dict['claims'].items()))
            output_dict['claims'] = OrderedDict(sorted(output_dict['claims'].items(),
                                                       key=dict_sorting_by_length))
            output_dict['categories'] = sorted(sorted(output_dict['categories']),
                                               key=list_sorting_by_length)
        return output_dict
    return False


def get_item_json(qid):
    """
    Get item json dictionary from qid
    Args:
        qid (str): Wikidata Identifier, ex: "Q1234"

    Returns:
        Dict: Returned value of WDItemEngine().wd_json_representation
    """
    try:
        item = WDItemEngine(wd_item_id=qid)
        return item.wd_json_representation
    except (ValueError, ConnectionAbortedError, Exception):
        logging.exception("Exception reading QID: %s", qid)
        return None


def get_item_property_counts(qid):
    """
    Count the number of values in a claim by property
    Args:
        qid (str): Wikidata Identifier, ex: "Q1234"

    Returns:
        Dict: {k(str): v(int)} where k is Wikidata Property identifier string and v is count
    """
    selected_item = get_item_json(qid)
    claims = get_claims_from_json(selected_item)
    counts = {}
    for pid, values in claims.items():
        counts[pid] = len(values)
    return counts


def get_claims_from_json(item_json):
    """
    Get claim dictionary from WD Item Json Representation
    Args:
        item_json (dict): Returned value of WDItemEngine().wd_json_representation

    Returns:
        Dictionary of {k:v} where k is property id and v is list of value dictionaries
    """
    return item_json.get('claims', {})


def get_references_from_item_json(item_json, cached_property_labels=None):
    """
    Get references from WD Item Json Representation
    Args:
        item_json (dict): Returned value of WDItemEngine().wd_json_representation
        cached_property_labels (Optional): Set of property label kv's

    Returns:
        [{}]: List of reference dictionaries
    """
    output = []
    json_references = item_json.get('references')
    if json_references:
        ref_list = json_references[0]
        for snak in ref_list['snaks-order']:
            pid = ref_list['snaks'][snak][0]['property']
            ref_val = parse_by_data_type(ref_list['snaks'][snak][0]['datavalue']['value'], cached_property_labels)
            output.append((pid, pid_label(pid, cached_property_labels), ref_val))
    return output


def parse_claims(claim, property_label, json_details, output_dict, cached_property_labels):
    """ Uses the json_details dictionary of a single claim and outputs
    the parsed data into the output_dict. """
    try:
        main_snak = json_details.get('mainsnak')
        if main_snak['snaktype'] == 'novalue' or 'datavalue' not in main_snak:
            return output_dict
        #  Parsing the statements & values by data type
        data_type = main_snak['datavalue']['type']
        data_value = main_snak['datavalue']['value']
        val, depth = get_value_of_claim(data_type, data_value, cached_property_labels)
        #  In the event the value is an image file name, convert the title to the image's url
        if claim in ["P18", "P154"]:
            val = get_wikimedia_image_url_from_title(val)
        #  Determining the 'category' of the item from the 'instance of' and 'subclass of' properties
        elif claim in ['P31', 'P279']:
            output_dict['categories'].append(val)
        if data_type == 'external-id':
            ex_id_key = (claim, property_label, val, format_url_from_property(claim, val))
            if ex_id_key in output_dict.get('ex-ids'):
                output_dict['ex-ids'][ex_id_key].append(val)
            else:
                output_dict['ex-ids'][ex_id_key] = [val]
        else:
            claim_key = (claim, property_label, depth)
            if claim_key in output_dict.get('claims'):
                output_dict['claims'][claim_key].append(val)
            else:
                output_dict['claims'][claim_key] = [val]
        references = get_references_from_item_json(json_details, cached_property_labels)
        if references:
            output_dict['refs'][(claim, val if type(val) is not list else val[0])] = references
    except (KeyError, Exception):
        logging.exception("Unexpected exception parsing claims.")
    return output_dict


def parse_by_data_type(data, cached_property_labels=None):
    """ Checks the data type of the current data value to determine how
    to return as a string or ID-label tuple. """
    data_type = type(data)
    if data_type is dict:
        if 'text' in data:
            return data['text']
        elif 'time' in data:
            return time_formatter(data.get('time'))
        elif 'entity-type' in data and 'id' in data:
            return id_to_label_list(data.get('id'), cached_property_labels)
    return data


def get_value_of_claim(data_type, data_value, cached_property_labels):
    """Uses a data type to determine how to format the value in the dictionary"""
    if data_type == 'string':
        return data_value, 1
    elif data_type == 'wikibase-entityid':
        entity_type = data_value.get('entity-type')
        if entity_type == 'item':
            return [data_value.get('id')], 2
        elif entity_type == 'property':
            val = 'P{}'.format(data_value.get('numeric-id'))
            return [val, pid_label(val, cached_property_labels)], 2
    elif data_type == 'time':
        return time_formatter(data_value['time']), 1
    elif data_type == 'quantity' and 'amount' in data_value:
        num = data_value.get('amount')
        try:
            return int(num), 1
        except ValueError:
            return float(num), 1
    elif data_type == 'monolingualtext':
        return '"{}" (language: {})'.format(data_value.get('text', ''), data_value.get('language', 'unknown')), 1
    return "Unable To Parse Value {}".format(data_type), 1


def id_to_label_list(wikidata_id, cached_property_labels):
    """Takes in an id (P## or Q##) and returns a list of that entity's label and id"""
    if wikidata_id[0].lower() == 'p':
        return [wikidata_id, pid_label(wikidata_id, cached_property_labels)]
    return [wikidata_id]


def pid_label(pid, cached_values):
    """Convert property identifier (P###) to a label and updates the cache."""
    if pid not in cached_values:
        prop = get_property(pid)
        default_label = "property {}".format(pid)
        property_label = prop['propertyLabel'].get('value', default_label) if prop else default_label
        cached_values[pid] = property_label
        return property_label
    return cached_values.get(pid)


def format_url_from_property(pid, value):
    """Inputs property identifier (P###) for a given url type, looks up that
    wikidata property id's url format (P1630) and creates a url with the value using the format"""
    value = value.strip()
    prop = get_property(pid)
    if 'formatter_url' in prop:
        return prop['formatter_url']['value'].replace("$1", value)
    return "unavailable"


def create_query_template(_string):
    flat_str = flatten_string(_string)
    return Template(flat_str)


# Register Template Queries Here
PROPERTY_QUERY_TEMPLATE = create_query_template(PROPERTY_QUERY)
