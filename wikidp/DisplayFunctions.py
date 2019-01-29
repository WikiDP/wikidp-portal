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
""" Template display helper functions. """
from collections import OrderedDict
import logging
from wikidataintegrator import wdi_core

from wikidp import APP
from wikidp.const import ConfKey
from wikidp.utils import (
    list_sorting_by_length,
    dict_sorting_by_length,
    time_formatter
)

from wikidp.controllers import (
    wikimedia as wikimedia_controller,
    api as api_controller
)

# Global Variables:
LANG = APP.config[ConfKey.WIKIDATA_LANG]
FALLBACK_LANG = APP.config[ConfKey.WIKIDATA_FB_LANG]


def item_detail_parse(qid):
    """Uses the JSON representation of wikidataintegrator to parse the item ID specified (qid)
    and returns a new dictionary of previewing information and a dictionary of property counts"""
    try:
        item = wdi_core.WDItemEngine(wd_item_id=qid)
    except:
        logging.exception("Exception reading QID: %s", qid)
        return False

    label = item.get_label(lang=LANG) if item.get_label(lang=LANG) != '' else item.get_label(lang=FALLBACK_LANG)
    item = item.wd_json_representation
    output_dict = {'label': [qid, label], 'claims':{}, 'refs':{},
                   'sitelinks':{}, 'aliases':[], 'ex-ids':{}, 'description':[],
                   'categories':[], 'properties':[], 'prop-counts':{}}
    count_dict = {}
    try:
        output_dict['aliases'] = [x['value'] for x in item['aliases'].get(LANG) or item['aliases'][FALLBACK_LANG]]
    except:
        pass
    try:
        output_dict['description'] = [x['value'] for x in item['descriptions'].get(LANG) or item['descriptions'][FALLBACK_LANG]]
    except:
        pass
    properties = api_controller.get_property([claim for claim in item['claims']], source="server", multiple=True)
    cached_property_labels = {prop['id']['value']: prop['propertyLabel']['value'] for prop in properties}
    for claim in item['claims']:
        count = 0
        property_label = cached_property_labels[claim]
        for json_details in item['claims'][claim]:
            count = parse_claims(claim, property_label, json_details, count, output_dict, cached_property_labels)
            if count > 0:
                count_dict[claim] = count
    output_dict['claims'] = OrderedDict(sorted(output_dict['claims'].items()))
    output_dict['claims'] = OrderedDict(sorted(output_dict['claims'].items(),
                                               key=dict_sorting_by_length))
    output_dict['categories'] = sorted(sorted(output_dict['categories']),
                                       key=list_sorting_by_length)
    output_dict['prop-counts'] = count_dict
    return output_dict

def parse_claims(claim, property_label, json_details, count, output_dict, cached_property_labels):
    """ Uses the json_details dictionary of a single claim and outputs
    the parsed data into the output_dict. """
    #Parsing references
    try:
        if json_details['mainsnak']['snaktype'] == 'novalue':
            return 0
        reference = []
        ref_num = 0
        if json_details['references'] != []:
            ref_list = json_details['references'][0]
            for snak in ref_list['snaks-order']:
                pid = ref_list['snaks'][snak][0]['property']
                ref_val = parse_by_datatype(ref_list['snaks'][snak][0]['datavalue']['value'], cached_property_labels)
                reference.append((pid, pid_label(pid, cached_property_labels), ref_val))
                ref_num += 1
        val = ["error at the "]
        size = 1
        #Parsing the statements & values by data taype
        if 'datavalue' in json_details['mainsnak']:
            data_type = json_details['mainsnak']['datavalue']['type']
            data_value = json_details['mainsnak']['datavalue']['value']
            val, size = get_value_of_claim(data_type, data_value, cached_property_labels)
        try:
            data_type = json_details['mainsnak']['datatype']
            if data_type == 'external-id':
                output_dict['ex-ids'][(claim, property_label, val, format_url_from_property(claim, val))].append(val)
            else:
                output_dict['claims'][(claim, property_label, size)].append(val)
            if ref_num > 0:
                output_dict['refs'][(claim, val[0])] = reference
        except:
            if data_type == 'external-id':
                output_dict['ex-ids'][(claim, property_label, val, format_url_from_property(claim, val))] = [val]
            else:
                output_dict['claims'][(claim, property_label, size)] = [val]
            if ref_num > 0:
                output_dict['refs'][(claim, val[0])] = reference
        #Determining the 'category' of the item from the 'instance of' and 'subclass of' properties
        if claim in ['P31', 'P279']:
            output_dict['categories'].append(val)
            #In the event the value is a image file, it converts the title to the image's url
        elif claim in ["P18", "P154"]:
            original = json_details['mainsnak']['datavalue']['value']
            output_dict["claims"][(claim, property_label, size)].append(wikimedia_controller.get_image_url_from_title(original))
            output_dict["claims"][(claim, property_label, size)].remove(original)
        count += 1
    except Exception as _e:
        logging.exception("Unexpected exception parsing claims.")
    return count

def parse_by_datatype(data, cached_property_labels=False):
    """ Checks the datatype of the current data value to determine how
    to return as a string or ID-label tuple. """
    data_type = type(data)
    if data_type is list:
        pass
    elif data_type is set:
        pass
    elif data_type is dict:
        keys = data.keys()
        if 'text' in keys:
            data = data['text']
        elif 'time' in keys:
            data = time_formatter(data['time'])
        elif 'entity-type' in keys:
            if 'id' in keys:
                data = id_to_label_list(data['id'], cached_property_labels)
    return data

def get_value_of_claim(data_type, data_value, cached_property_labels):
    """Uses a data type to determine how to format the value in the dictionary"""
    val, size = ["error at the "], 1
    if data_type == 'string':
        return data_value, 1
    elif data_type == 'wikibase-entityid':
        if data_value['entity-type'] == 'item':
            val = data_value['id']
            val = [val]
            size = 2
        elif data_value['entity-type'] == 'property':
            val = 'P'+str(data_value['numeric-id'])
            val = [val, pid_label(val, cached_property_labels)]
            size = 2
        else:
            val = [val[0]+"entity-type level"]
    elif data_type == 'time':
        val = time_formatter(data_value['time'])
    else:
        val = [val[0] + "type level " + data_type]
    return val, size


def id_to_label_list(wikidata_id, cached_property_labels=False):
    """Takes in an id (P## or Q##) and returns a list of that entity's label and id"""
    if wikidata_id[0].lower() == 'p':
        return [wikidata_id, pid_label(wikidata_id, cached_property_labels)]
    return [wikidata_id]
    # return [wikidata_id, qid_label(wikidata_id)]

def pid_label(pid, cached_values=False):
    """Convert property identifier (P###) to a label and updates the cache."""
    if cached_values is not False and pid in cached_values:
        return cached_values[pid]
    property = api_controller.get_property(pid, source='server')
    if property is False:
        property_label = "property "+pid
    else:
        property_label = property['propertyLabel']['value']
    if cached_values is not False:
        cached_values[pid] = property_label
    return property_label


def format_url_from_property(pid, value):
    """Inputs property identifier (P###) for a given url type, lookes up that
    pid's url format (P1630) and creates a url with the value using the format"""
    value = value.strip()
    property = api_controller.get_property(pid, source='server')
    if 'formatter_url' in property:
        return property['formatter_url']['value'].replace("$1", value)
    else:
        return "unavailable"


def qid_to_basic_details(qid):
    """Input item qid and returns a tuple: (qid, label, description) using WikiDataIntegrator"""
    item = wdi_core.WDItemEngine(wd_item_id=qid)
    item_id = item.wd_item_id.replace("'", "&#39;")
    label = item.get_label(lang=LANG) if item.get_label(lang=LANG) != '' else item.get_label(lang=FALLBACK_LANG)
    desc = (item.get_description(lang=LANG) or item.get_description(lang=FALLBACK_LANG)).replace("'", "&#39;")
    aliases = item.get_aliases(lang=LANG) or item.get_aliases(lang=FALLBACK_LANG)
    return {"id": item_id, "label": label, "description": desc, "aliases": aliases}
