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
"""Search Controller Functions and Helpers for WikiDP."""

import logging
import re

from wikidataintegrator.wdi_core import WDItemEngine

from wikidp.models import (
    FileFormatExtSearchResult,
    PuidSearchResult,
)
from wikidp.utils import (
    dedupe_by_key,
    LANG,
    item_detail_parse,
)


def get_search_result_context(search_string):
    """
    Get search results from a substring.
    Args:
        search_string (str):

    Returns (List[Optional[Dict]]):

    """
    # Check if searching by file extension
    context = [
        {'qid': res.format, 'label': res.label, 'description': res.description}
        for res in FileFormatExtSearchResult.search(search_string)
    ]
    # Check if searching with PUID
    # pylint: disable=W1401
    if re.search("[x-]?fmt/\d+", search_string) is not None:
        context.extend([
            {'qid': res.format, 'label': res.label,
             'description': res.description}
            for res in PuidSearchResult.search_puid(search_string, lang=LANG)
        ])
    # Search Wikidata natively
    context.extend(search_result_list(search_string))
    return dedupe_by_key(context, 'qid')


def search_result_list(string):
    """
    Use wikidataintegrator to generate a list of similar items based on a
    text search and returns a list of (qid, Label, description, aliases)
    dictionaries
    """
    result_qid_list = WDItemEngine.get_wd_search_results(string, language=LANG)
    output = []
    for qid in result_qid_list[:10]:
        item = item_detail_parse(qid, with_claims=False)
        if item:
            output.append(item)
    return output


def get_search_by_puid_context(puid):
    """ Perform an item search by PUID. """
    new_puid = puid.replace('_', '/')
    logging.debug("Searching for PUID: %s", new_puid)
    results = PuidSearchResult.search_puid(new_puid, lang=LANG)
    return new_puid, results
