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
"""Flask application custom url converters for Wikidata portal."""
from werkzeug.routing import BaseConverter

from wikidp.config import APP
from wikidp.const import ConfKey


ITEM_REGEX = APP.config[ConfKey.ITEM_REGEX]
PROPERTY_REGEX = APP.config[ConfKey.PROPERTY_REGEX]


class WikidataItemConverter(BaseConverter):
    """Custom Routing Mapping for Wikidata Item Identifiers such as Q1234."""

    def __init__(self, url_map):
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

    def __init__(self, url_map):
        """Use default settings with just applied regex."""
        super(WikidataPropertyConverter, self).__init__(url_map)
        self.regex = PROPERTY_REGEX

    def to_python(self, value):
        """Value should be string with capital letters for consistency."""
        return value.upper()

    def to_url(self, value):
        """Value should be string with capital letters for consistency."""
        return value.upper()


# Custom Routing Converters
APP.url_map.converters['item'] = WikidataItemConverter
APP.url_map.converters['prop'] = WikidataPropertyConverter
