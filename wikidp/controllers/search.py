"""Search Controller Functions and Helpers for WikiDP."""

import logging
import re

from wikidataintegrator.wdi_core import WDItemEngine

from wikidp.model import PuidSearchResult
from wikidp.DisplayFunctions import (
    LANG,
    qid_to_basic_details
)


def get_search_result_context(search_string):
    context = []
    # Check if searching with PUID
    if re.search("[x-]?fmt/\d+", search_string) is not None:
        result = PuidSearchResult.search_puid(search_string, lang=LANG)
        for res in result:
            item = qid_to_basic_details(res.format)
            context.append({
                'id': res.format,
                'label': res.label,
                'description': item.get('description', "This item does not have a description")
            })
    context += search_result_list(search_string)
    return context


def search_result_list(string):
    """
    Use wikidataintegrator to generate a list of similar items based on a
    text search and returns a list of (qid, Label, description, aliases)
    dictionaries
    """
    options = WDItemEngine.get_wd_search_results(string, language=LANG)
    if len(options) > 10:
        options = options[:10]
    output = []
    for opt in options:
        try:
            opt = qid_to_basic_details(opt)
            output.append(opt)
        # skip those that wdi can not process
        except Exception:
            logging.exception("Untyped exception caught")
    return output


def get_search_by_puid_context(puid):
    new_puid = puid.replace('_', '/')
    logging.debug("Searching for PUID: %s", new_puid)
    results = PuidSearchResult.search_puid(new_puid, lang=LANG)
    return new_puid, results
