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
"""Model classes to glue queries to return types."""
import logging

from wikidataintegrator import wdi_core

class FileFormat(object):
    """Encapsulates a file format plus widata query magic for formats."""
    def __init__(self, qid, name, media_types=None):
        self._qid = qid
        self._name = name
        self._media_types = media_types if media_types is not None else []

    @property
    def qid(self):
        """The wikidata item id."""
        return self._qid

    @property
    def name(self):
        """The name of the format, equivalent to the WikiData label."""
        return self._name

    @property
    def media_types(self):
        """A list of MediaTypes associated with the format."""
        return self._media_types

    def __str__(self):
        ret_val = []
        ret_val.append("FileFormat : [qid=")
        ret_val.append(self.qid)
        ret_val.append(", name=")
        ret_val.append(self.name)
        ret_val.append(", media_types=[")
        ret_val.append('|'.join(self.media_types))
        ret_val.append("]]")
        return "".join(ret_val)

    @classmethod
    def list_formats(cls):
        """Queries Wikdata for formats and returns a list of FileFormat instances."""
        query = """
SELECT DISTINCT ?idFileFormat ?idFileFormatLabel
                (GROUP_CONCAT(DISTINCT ?mediaType; SEPARATOR="|") AS ?mediaTypes)
WHERE
{
    ?idFileFormat wdt:P31 wd:Q235557
    OPTIONAL {
        ?idFileFormat wdt:P1163 ?mediaType .
    }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
}
GROUP BY ?idFileFormat ?idFileFormatLabel
ORDER BY ?idFileFormatLabel
            """
        results_json = wdi_core.WDItemEngine.execute_sparql_query(query)
        results = [cls(x['idFileFormat']['value'].replace('http://www.wikidata.org/entity/', ''),
                       x['idFileFormatLabel']['value'],
                       x['mediaTypes']['value'].split('|'))
                   for x in results_json['results']['bindings']]
        return results

class PuidSearchResult(object):
    """Encapsulates a file format plus widata query magic for formats."""
    def __init__(self, format, label, puid):
        self._format = format
        self._label = label
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
    def puid(self):
        """The PUID of the format."""
        return self._puid

    def __str__(self):
        ret_val = []
        ret_val.append("PuidSearchResult : [format=")
        ret_val.append(self.format)
        ret_val.append(", label=")
        ret_val.append(self.label)
        ret_val.append(", puid=")
        ret_val.append(self.puid)
        ret_val.append("]")
        return "".join(ret_val)

    @classmethod
    def search_puid(cls, puid):
        """Queries Wikdata for formats and returns a list of FileFormat instances."""
        query = [
            "SELECT DISTINCT ?format ?formatLabel ?puid ",
            "WHERE { ",
            "?format wdt:P2748 ?puid  FILTER (?puid = '{}') . ".format(puid),
            "SERVICE wikibase:label {bd:serviceParam wikibase:language 'en' .}",
            "}"
            ]
        results_json = wdi_core.WDItemEngine.execute_sparql_query("".join(query))
        logging.debug(str(results_json))
        results = [cls(x['format']['value'].replace('http://www.wikidata.org/entity/', ''),
                       x['formatLabel']['value'],
                       x['puid']['value'])
                   for x in results_json['results']['bindings']]
        return results