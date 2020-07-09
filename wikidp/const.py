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
"""Constants used across BitCurator modules.

These need to map to the names used in the default config file, but better
than multiple hardcoded strings in code.
"""
ENTITY_URL_PATTERN = 'http://www.wikidata.org/entity/$1'
PROPERTY_REGEX = r'(P|p)\d+'
PUID_REGEX = r"[x-]?fmt/\d+"
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
    ("ja", "日本語 (Japanese)"),
    ("hi", "हिन्दी (Hindi)"),
    ("lb", "Lëtzebuergesch (Luxembourgish)")
]
WIKIMEDIA_COMMONS_BASE_URL = "https://commons.wikimedia.org"
WIKIMEDIA_COMMONS_API_URL = f"{WIKIMEDIA_COMMONS_BASE_URL}/w/api.php"


# pylint: disable=R0903
class ConfKey:
    """Config key string constants."""

    ITEM_REGEX = 'ITEM_REGEX'
    LOG_FILE = 'LOG_FILE'
    LOG_FORMAT = 'LOG_FORMAT'
    PORT = "PORT"
    PROPERTY_REGEX = 'PROPERTY_REGEX'
    STATIC_DIR = "STATIC_DIR"
    MEDIAWIKI_API_URL = 'MEDIAWIKI_API_URL'
    SPARQL_ENDPOINT_URL = 'SPARQL_ENDPOINT_URL'
    WIKIBASE_LANGUAGE = 'WIKIBASE_LANGUAGE'
    WIKIDATA_FB_LANG = 'WIKIDATA_FB_LANG'
    WIKIDATA_LANG = 'WIKIDATA_LANG'
    WIKIDATA_PASSWORD = 'WIKIDATA_PASSWORD'
    WIKIDATA_USER_NAME = 'WIKIDATA_USER_NAME'


class WDEntityField:
    """Enum of field names for describing Wikidata Entities."""

    ALIASES = 'aliases'
    LABEL = 'label'
    DESCRIPTION = 'description'
    QID = 'qid'
    CLAIMS = 'claims'
    EXTERNAL_LINKS = 'external_links'
    CATEGORIES = 'categories'
    REFERENCES = 'references'
    QUALIFIERS = 'qualifiers'
