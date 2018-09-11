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

from unittest import TestCase

from wikidataintegrator import wdi_core
from wikidataintegrator.wdi_core import WDItemEngine

from wikidp.model import FileFormat, PuidSearchResult

class WikidataTests(TestCase):
    def test_format_read(self):
        """Queries Wikidata for formats and returns a list of FileFormat instances."""
        results = FileFormat.list_formats()
        assert len(results) > 0, \
        'Format read returned no results'

    def test_sandbox_mime_read(self):
        mediawiki_api_url = 'https://test.wikidata.org/w/api.php'
        sparql_endpoint_url = 'https://test.wikidata.org/proxy/wdqs/bigdata/namespace/wdq/sparql'
        wiki_sandbox = WDItemEngine.wikibase_item_engine_factory(mediawiki_api_url, sparql_endpoint_url)
        sandbox_results = PuidSearchTest.search_mime(wiki_sandbox, "text/plain")
        results = PuidSearchTest.search_mime(wdi_core.WDItemEngine, "text/plain")
        assert len(sandbox_results) == len(results), \
        'There should be no PUID results in the sandbox.'

    def test_item_write(self):
        assert True

class PuidSearchTest(object):
    """Encapsulates a file format plus widata query magic for formats."""
    def __init__(self, wd_format, label, mime, puid):
        self._format = wd_format
        self._label = label
        self._mime = mime
        self._puid = puid

    @property
    def format(self):
        """The wikidata item the format field."""
        return self._format

    @property
    def label(self):
        """The formats WikiData label."""
        return self._label

    @property
    def mime(self):
        """The MIME type of the format."""
        return self._mime

    @property
    def puid(self):
        """The PUID of the format."""
        return self._puid

    def __str__(self):
        ret_val = []
        ret_val.append("PuidSearchResult : [format=")
        ret_val.append(self.format)
        ret_val.append(", label=")
        ret_val.append(self.label)
        ret_val.append(", MIME=")
        ret_val.append(self.mime)
        ret_val.append(", puid=")
        ret_val.append(self.puid)
        ret_val.append("]")
        return "".join(ret_val)

    @classmethod
    def search_puid(cls, wdengine, puid, lang="en"):
        """Queries Wikdata for formats and returns a list of FileFormat instances."""
        query = cls._concat_query("VALUES ?puid {{ '{}' }}".format(puid), lang)
        results_json = wdengine.execute_sparql_query(query)
        return cls._assemble_results(results_json)

    @classmethod
    def search_mime(cls, wdengine, mime, lang="en"):
        """Queries Wikdata for formats and returns a list of FileFormat instances."""
        query = cls._concat_query("VALUES ?mime {{ '{}' }}".format(mime), lang)
        results_json = wdengine.execute_sparql_query(query)
        return cls._assemble_results(results_json)

    @staticmethod
    def _concat_query(values_clause="", lang="en"):
        query = [
            "SELECT DISTINCT ?format ?formatLabel ?mime ?puid",
            "WHERE {",
            "?format wdt:P2748 ?puid.",
            "?format wdt:P1163 ?mime.",
            "SERVICE wikibase:label {{ bd:serviceParam wikibase:language '{}' }}".format(lang)
            ]
        query.append(values_clause)
        query.append("}")
        return " ".join(query)

    @staticmethod
    def _assemble_results(results_json):
        results = [PuidSearchResult(
            x['format']['value'].replace('http://www.wikidata.org/entity/', ''),
            x['formatLabel']['value'],
            x['mime']['value'],
            x['puid']['value'])
                   for x in results_json['results']['bindings']]
        return results
