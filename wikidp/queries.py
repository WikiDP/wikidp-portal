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
"""Ugly hardcoded queries until a better method is found."""
QUERIES = {
    'list-formats' :
    """
    SELECT DISTINCT ?idExtension ?extension ?mediaType ?idExtensionLabel
    WHERE
    {
        ?idExtension wdt:P31 wd:Q235557
        ; wdt:P1195 ?extension .
        OPTIONAL { ?idExtension wdt:P1163 ?mediaType }
        SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
    }
    ORDER BY ?extension ?mediaType
    """
}
