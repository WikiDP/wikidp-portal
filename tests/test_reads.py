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
"""Unit tests for WikiData reads."""
from unittest import TestCase

import pywikibot

from wikidataintegrator import wdi_core
from wikidataintegrator.wdi_core import WDItemEngine

from wikidp.model import FileFormat, PuidSearchResult
SANDBOX_API_URL = 'https://test.wikidata.org/w/'
SANDBOX_SPARQL_URL = 'https://test.wikidata.org/proxy/wdqs/bigdata/namespace/wdq/'
SITE = pywikibot.Site("test", "wikidata")
REPO = SITE.data_repository()

class WikidataTests(TestCase):
    def test_format_read(self):
        """Queries Wikidata for formats and returns a list of FileFormat instances."""
        results = FileFormat.list_formats()
        assert results, \
        'Format read returned no results'

    def test_new_item(self):
        new_item = pywikibot.ItemPage(SITE)
        labels = {"en": "Carl Wilson", "de": "Carl Wilson"}
        new_item.editLabels(labels=labels, summary="Adding labels")
        my_item_id = new_item.getID()
        item = pywikibot.ItemPage(REPO, my_item_id)
        item.get()
        assert item.labels['en'] == 'Carl Wilson'
        assert item.labels['de'] == 'Carl Wilson'
