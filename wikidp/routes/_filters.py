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
"""Flask application custom template filters for Wikidata portal."""
from urllib.parse import quote_plus

from markupsafe import Markup

from wikidp.config import APP
from wikidp.const import ENTITY_URL_PATTERN
from wikidp.utils import (
    get_pid_from_string,
    get_qid_from_string,
)


@APP.template_filter('url_encode')
def template_filter_url_encode(to_encode):
    """Carry out URL encoding on template filter URL."""
    if isinstance(to_encode, Markup):
        to_encode = to_encode.unescape()
    to_encode = to_encode.encode('utf8')
    to_encode = quote_plus(to_encode)
    return Markup(to_encode)


@APP.template_filter('qlabel_attributes')
def template_qlabel_attributes(url):
    """
    Add tag attributes for qlabel.js.

    Args:
        url (str): Text for the label and titles

    Returns:
        str: HTML tag attributes
    """
    return "class=qlabel its-ta-ident-ref={}".format(url)


@APP.template_filter('entity_url')
def template_filter_entity_url(entity_id):
    """
    Convert Item of Property string to Wikidata URL.

    Args:
        entity_id (str): Item ('Q1234') or Property ('P1234') identifier

    Returns:
        str: http url destination for the entity
    """
    valid_string = get_qid_from_string(entity_id)
    if not valid_string:
        valid_string = get_pid_from_string(entity_id)
    return ENTITY_URL_PATTERN.replace('$1', valid_string) if valid_string else '#'
