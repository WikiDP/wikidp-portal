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
WIKIDATA_ENTITY_BASE_URL = "https://wikidata.org/entity"
WIKIMEDIA_COMMONS_BASE_URL = "https://commons.wikimedia.org"
WIKIMEDIA_COMMONS_API_URL = f"{WIKIMEDIA_COMMONS_BASE_URL}/w/api.php"
WIKIDATA_DATETIME_FORMAT = '+%Y-%m-%dT%H:%M:%SZ'


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
    OAUTH_MEDIAWIKI_URL = 'OAUTH_MEDIAWIKI_URL'
    SPARQL_ENDPOINT_URL = 'SPARQL_ENDPOINT_URL'
    USER_AGENT = 'USER_AGENT'
    WIKIBASE_LANGUAGE = 'WIKIBASE_LANGUAGE'
    WIKIDATA_FB_LANG = 'WIKIDATA_FB_LANG'
    WIKIDATA_LANG = 'WIKIDATA_LANG'
    WIKIDATA_PASSWORD = 'WIKIDATA_PASSWORD'
    WIKIDATA_USER_NAME = 'WIKIDATA_USER_NAME'
    WIKIDP_CONSUMER_KEY = 'WIKIDP_CONSUMER_KEY'
    WIKIDP_CONSUMER_SECRET = 'WIKIDP_CONSUMER_SECRET'


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
    URL = 'url'


DEFAULT_PID_LIST = [
    "P9151",
    "P9100",
    "P8778",
    "P8709",
    "P8443",
    "P8205",
    "P7967",
    "P7966",
    "P7510",
    "P7126",
    "P6931",
    "P6665",
    "P6366",
    "P5688",
    "P5398",
    "P5247",
    "P5047",
    "P4969",
    "P4839",
    "P4506",
    "P4460",
    "P4428",
    "P4162",
    "P4152",
    "P3984",
    "P3966",
    "P3827",
    "P3743",
    "P3641",
    "P3499",
    "P3473",
    "P3463",
    "P3454",
    "P3442",
    "P3381",
    "P3374",
    "P3266",
    "P2748",
    "P2537",
    "P2283",
    "P2209",
    "P2179",
    "P2093",
    "P2078",
    "P2037",
    "P1889",
    "P1814",
    "P1813",
    "P1547",
    "P1482",
    "P1366",
    "P1365",
    "P1343",
    "P1065",
    "P973",
    "P856",
    "P854",
    "P348",
    "P144",
    "P856",
    "P527",
    "P577",
    "P1889",
    "P571",
    "P18",
    "P275",
    "P154",
    "P503",
    "P277",
    "P138",
]
