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
import os
import errno
import json
import pickle
import urllib.request
import datetime
from lxml import html
import pywikibot
import requests
from wikidataintegrator import wdi_core

from wikidp import APP
from wikidp.const import ConfKey

# Global Variables:
URL_CACHE, PID_CACHE = {}, {}
LANG = APP.config[ConfKey.WIKIDATA_LANG]
FALLBACK_LANG = APP.config[ConfKey.WIKIDATA_FB_LANG]
CACHE_DIR = APP.config['CACHE_DIR']

def search_result_list(string):
    """Uses wikidataintegrator to generate a list of similar items based on a text search
    and returns a list of (qid, Label, description, aliases) dictionaries"""
    options = wdi_core.WDItemEngine.get_wd_search_results(string, language=LANG)
    if len(options) > 10:
        options = options[:10]
    output = []
    for opt in options:
        try:
            opt = qid_to_basic_details(opt)
            output.append(opt)
        # skip those that wdi can not process
        except Exception as _e:
            logging.exception("Untyped exception caught")
    return output

def item_detail_parse(qid):
    """Uses the JSON representation of wikidataintegrator to parse the item ID specified (qid)
    and returns a new dictionary of previewing information and a dictionary of property counts"""
    try:
        item = wdi_core.WDItemEngine(wd_item_id=qid)
    except:
        logging.exception("Exception reading QID: %s", qid)
        return None
    load_caches()
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
    for claim in item['claims']:
        count = 0
        label = pid_label(claim)
        for json_details in item['claims'][claim]:
            count = parse_claims(claim, label, json_details, count, output_dict)
            if count > 0:
                count_dict[claim] = count
    output_dict['claims'] = OrderedDict(sorted(output_dict['claims'].items()))
    output_dict['claims'] = OrderedDict(sorted(output_dict['claims'].items(),
                                               key=dict_sorting_by_length))
    output_dict['categories'] = sorted(sorted(output_dict['categories']),
                                       key=list_sorting_by_length)
    save_caches()
    output_dict['prop-counts'] = count_dict
    return output_dict

def parse_claims(claim, label, json_details, count, output_dict):
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
                ref_val = parse_by_datatype(ref_list['snaks'][snak][0]['datavalue']['value'])
                reference.append((pid, pid_label(pid), ref_val))
                ref_num += 1
        val = ["error at the "]
        size = 1
        #Parsing the statements & values by data taype
        if 'datavalue' in json_details['mainsnak']:
            data_type = json_details['mainsnak']['datavalue']['type']
            data_value = json_details['mainsnak']['datavalue']['value']
            val, size = get_value_of_claim(data_type, data_value)
        try:
            data_type = json_details['mainsnak']['datatype']
            if data_type == 'external-id':
                output_dict['ex-ids'][(claim, label, val, url_formatter(claim, val))].append(val)
            else:
                output_dict['claims'][(claim, label, size)].append(val)
            if ref_num > 0:
                output_dict['refs'][(claim, val[0])] = reference
        except:
            if data_type == 'external-id':
                output_dict['ex-ids'][(claim, label, val, url_formatter(claim, val))] = [val]
            else:
                output_dict['claims'][(claim, label, size)] = [val]
            if ref_num > 0:
                output_dict['refs'][(claim, val[0])] = reference
        #Determining the 'category' of the item from the 'instance of' and 'subclass of' properties
        if claim in ['P31', 'P279']:
            output_dict['categories'].append(val)
            #In the event the value is a image file, it converts the title to the image's url
        elif claim in ["P18", "P154"]:
            original = json_details['mainsnak']['datavalue']['value']
            output_dict["claims"][(claim, label, size)].append(image_url(original))
            output_dict["claims"][(claim, label, size)].remove(original)
        count += 1
    except Exception as _e:
        logging.exception("Unexpected exception parsing claims.")
    return count

def parse_by_datatype(data):
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
                data = id_to_label_list(data['id'])
    return data

def get_value_of_claim(data_type, data_value):
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
            val = [val, pid_label(val)]
            size = 2
        else:
            val = [val[0]+"entity-type level"]
    elif data_type == 'time':
        val = time_formatter(data_value['time'])
    else:
        val = [val[0] + "type level " + data_type]
    return val, size

def _setup_cache_dir():
    try:
        os.makedirs(CACHE_DIR)
    except OSError as _e:
        if _e.errno != errno.EEXIST:
            logging.exception("Cannot create cache directory %s", CACHE_DIR)
            raise

def load_caches():
    """Uses pickle to load all caching files as global variables"""
    logging.debug("Loading the caches with LANG %s", LANG)
    global URL_CACHE, PID_CACHE

    URL_CACHE = _pickle_cache_read("url-formats")
    PID_CACHE = _pickle_cache_read("property-labels")

def _pickle_cache_read(cache_name):
    pickle_file = os.path.join(CACHE_DIR, cache_name)
    try:
        with open(pickle_file, "rb") as _f:
            return pickle.load(_f)
    except FileNotFoundError:
        logging.info("Cache file not found: %s.", pickle_file)
    return {}

def save_caches():
    """Uses pickle to save global variables to caching files in order to update"""
    global URL_CACHE, PID_CACHE
    _pickle_cache_persist("url-formats", URL_CACHE)
    _pickle_cache_persist("property-labels", PID_CACHE)

def _pickle_cache_persist(cache_name, cache_dict):
    pickle_file = os.path.join(CACHE_DIR, cache_name)
    with open(pickle_file, "wb") as _f:
        pickle.dump(cache_dict, _f)

def id_to_label_list(wikidata_id):
    """Takes in an id (P## or Q##) and returns a list of that entity's label and id"""
    if wikidata_id[0].lower() == 'p':
        return [wikidata_id, pid_label(wikidata_id)]
    return [wikidata_id]
    # return [wikidata_id, qid_label(wikidata_id)]

def qid_label(qid):
    """Converts item identifier (Q###) to a label and updates the cache"""
    ## TO DO: Add step to try using wikidataintegrator as second option
    try:
        item = pywikibot.ItemPage(pywikibot.Site('wikidata', 'wikidata').data_repository(), qid)
        item.get()
        label = item.labels[LANG]
        return label
    except:
        try:
            item = pywikibot.ItemPage(pywikibot.Site('wikidata', 'wikidata').data_repository(), qid)
            item.get()
            label = item.labels.get(LANG, item.labels[FALLBACK_LANG]) # get the item in the language or in the fallback
            return label
        except:
            logging.exception("Unexpected exception finding QID label: %s", qid)
            return "Unknown Item Label"


def pid_label(pid):
    """Converts property identifier (P###) to a label and updates the cache"""
    global PID_CACHE
    try:
        return PID_CACHE[pid]
    except:
        try:
            # Use the API in order to get the full Property in JSON with all the language alternatives
            payload = {
                'action': 'wbgetentities',
                'ids': pid,
                'languages': '|'.join([LANG, FALLBACK_LANG]),
                'languagefallback': 'true',
                'props': 'labels',
                'format': 'json'
            }
            page = requests.get('https://www.wikidata.org/w/api.php', params=payload)
            jpage = page.json()
            labels=jpage['entities'][pid]['labels']
            title = labels.get(LANG, labels.get(FALLBACK_LANG))['value']
            # title = title[0][:-10]
            PID_CACHE[pid] = title
            return title
        except:
            logging.exception("Error finding property label: %s", pid)
            return "Unknown Property Label"

def time_formatter(time):
    """Converts wikidata's time json to a human readable string"""
    try:
        return datetime.datetime.strptime(time, '+%Y-%m-%dT%H:%M:%SZ').strftime("%A, %B %-d, %Y")
    except:
        return time

def url_formatter(pid, value):
    """Inputs property identifier (P###) for a given url type, lookes up that
    pid's url format (P1630) and creates a url with the value using the format"""
    global URL_CACHE
    value = value.strip()
    if pid in URL_CACHE:
        base = URL_CACHE[pid]
    else:
        try:
            url = urllib.request.urlopen("https://www.wikidata.org/wiki/Special:EntityData/%s.json"%(pid))
            base = json.loads(url.read().decode())
            URL_CACHE[pid] = base['entities'][pid]['claims']['P1630'][0]['mainsnak']['datavalue']['value']
        except:
            return "unavailable"
    base = base.replace("$1", value)
    return base

def image_url(title):
    """Converts the title of an image to the url location of that file it describes"""
    # TO DO: Url's do not work with non-ascii characters
    #    For example, the title of the image for Q267193 [Submlime Text]
    #    is "Скриншот sublime text 2.png"
    title = title.replace(" ", "_")
    url = "https://commons.wikimedia.org/w/api.php?action=query&prop=imageinfo&iiprop=url&titles=File:%s&format=json"%(title)
    try:
        url = urllib.request.urlopen(url)
        base = json.loads(url.read().decode())["query"]["pages"]
        for item in base:
            out = base[item]["imageinfo"][0]["url"]
        return out
    except:
        return "https://commons.wikimedia.org/wiki/File:"+title

def list_sorting_by_length(elem):
    """Auxiliary sorting key function at the list level"""
    return len(elem[0])

def dict_sorting_by_length(elem):
    """Auxiliary sorting key function at the dictionary level"""
    return len(elem[0][0])

def caching_label(label_id, label, file_name):
    """Auxiliary function to cache information {not currently called by any function}"""
    url = "wikidp/caches/"+file_name
    props = pickle.load(open(url, "rb"))
    props[label_id] = label
    pickle.dump(props, open(url, "wb"))

def qid_to_basic_details(qid):
    """Input item qid and returns a tuple: (qid, label, description) using WikiDataIntegrator"""
    item = wdi_core.WDItemEngine(wd_item_id=qid)
    label = item.get_label(lang=LANG) if item.get_label(lang=LANG) != '' else item.get_label(lang=FALLBACK_LANG)
    return {
        "id": item.wd_item_id,
        "label": label.replace("'", "&#39;"),
        "description": (item.get_description(lang=LANG) or item.get_description(lang=FALLBACK_LANG)).replace("'","&#39;"),
        "aliases": item.get_aliases(lang=LANG) or item.get_aliases(lang=FALLBACK_LANG)
    }

_setup_cache_dir()
load_caches()

# Testing function calls/data structure references:
# -------------------------------------------------
# search_result_list("Debian")
# search_result_list("google")
# item_detail_parse("Q131346")
# ('P31', 'Instance of', 2)
# ('P279', 'Subclass of', 2)
# item_detail_parse("Q7593")
