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
""" Flask application custom url converters for Wikidata portal. """
from wikidp import APP
from wikidp.utils import ITEM_REGEX, PROPERTY_REGEX
from werkzeug.routing import BaseConverter


class WikidataItemConverter(BaseConverter):
    """Custom Routing Mapping for Wikidata Item Identifiers such as Q1234."""

    def __init__(self, url_map, randomify=False):
        """Use default settings with just applied regex."""
        super(WikidataItemConverter, self).__init__(url_map)
        self.regex = ITEM_REGEX

    def to_python(self, value):
        """Value should be string with capital letters for consistency."""
        return value.upper()

    def to_url(self, value):
        """Value should be string with capital letters for consistency."""
        return value.upper()


class WikidataPropertyConverter(BaseConverter):
    """Custom Routing Mapping for Wikidata Property Identifiers such as P11."""

    def __init__(self, url_map, randomify=False):
        """Use default settings with just applied regex."""
        super(WikidataItemConverter, self).__init__(url_map)
        self.regex = PROPERTY_REGEX

    def to_python(self, value):
        """Value should be string with capital letters for consistency."""
        return value.upper()

    def to_url(self, value):
        """Value should be string with capital letters for consistency."""
        return value.upper()


APP.url_map.converters['item'] = WikidataItemConverter
APP.url_map.converters['property'] = WikidataPropertyConverter
