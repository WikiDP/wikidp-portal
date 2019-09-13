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
"""Constants used across BitCurator modules.
These need to map to the names used in the default config file, but better
than multiple hardcoded strings in code.
"""
ENTITY_URL_PATTERN = 'http://www.wikidata.org/entity/$1'
ITEM_REGEX = r'(Q|q)\d+'
PROPERTY_REGEX = r'(P|p)\d+'
LANG = 'en'
FALLBACK_LANG = 'en'
DEFAULT_UI_LANGUAGES = [
    (LANG, "English"),
    ("fr", "français (French)"),
    ("es", "español (Spanish)"),
    ("de", "Deutsch (German)"),
    ("da", "dansk (Danish)"),
    ("nl", "Nederlands (Dutch)"),
    ("zh", "汉语 (Chinese)"),
    ("ar", "العربية (Arabic)"),
    ("it", "italiano (Italian)"),
    ("lv", "latviešu valoda (Latvian)"),
    ("et", "eesti keel (Estonian)"),
    ("fi", "suomi (Finnish)"),
    ("pt", "português (Portuguese)"),
    ("sv", "svenska (Swedish)"),
    ("no", "Norsk (Norwegian)"),
    ("ja", "日本語 (Japanese)")
    ("hi", "हिन्दी (Hindi)")
    ("lb", "Lëtzebuergesch (Luxembourgish)")
]


class ConfKey():
    """Config key string constants"""
    LOG_FORMAT = 'LOG_FORMAT'
    LOG_FILE = 'LOG_FILE'
    WIKIDATA_LANG = 'WIKIDATA_LANG'
    WIKIDATA_FB_LANG = 'WIKIDATA_FB_LANG'
    WIKIBASE_LANGUAGE = 'WIKIBASE_LANGUAGE'
    ITEM_REGEX = 'ITEM_REGEX'
    PROPERTY_REGEX = 'PROPERTY_REGEX'
