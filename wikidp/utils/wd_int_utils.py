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
"""Module to hold all WikiDataIntegrator routines for dependency management."""
import logging
from wikidataintegrator.wdi_core import WDItemEngine

from wikidp.config import APP
from wikidp.const import ConfKey

MEDIAWIKI_API_URL = APP.config[ConfKey.MEDIAWIKI_API_URL]
SPARQL_ENDPOINT_URL = APP.config[ConfKey.SPARQL_ENDPOINT_URL]


def process_query_string(query):
    """Use WikiDataIntegrator Engine to process a SPARQL Query."""
    result = WDItemEngine.execute_sparql_query(query,
                                               endpoint=SPARQL_ENDPOINT_URL)
    bindings = result['results'].get('bindings')
    return _format_wikidata_bindings(bindings)


def _format_wikidata_bindings(bindings):
    return [{k: v.get('value') for k, v in res.items()} for res in bindings]


def get_item_json(qid):
    """
    Get item json dictionary from qid.

    Args:
        qid (str): Wikidata Identifier, ex: "Q1234"

    Returns:
        Dict: Returned value of WDItemEngine().wd_json_representation
    """
    try:
        item = WDItemEngine(wd_item_id=qid,
                            mediawiki_api_url=MEDIAWIKI_API_URL,
                            sparql_endpoint_url=SPARQL_ENDPOINT_URL)
        return item.wd_json_representation
    except (ValueError, ConnectionAbortedError):
        logging.exception("Exception reading QID: %s", qid)
        return None
