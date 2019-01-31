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
""" Flask application custom template filters for Wikidata portal. """
from markupsafe import Markup
from urllib.parse import quote_plus


from wikidp import APP
from wikidp.const import (
    ITEM_URL_PATTERN,
    PROPERTY_URL_PATTERN,
)
from wikidp.utils import (
    get_pid_from_string,
    get_qid_from_string,
    remove_extension_from_filename,
)


@APP.template_filter('url_encode')
def template_filter_url_encode(s):
    if type(s) == 'Markup':
        s = s.unescape()
    s = s.encode('utf8')
    s = quote_plus(s)
    return Markup(s)


@APP.template_filter('file_to_label')
def template_filter_file_to_label(filename):
    output = remove_extension_from_filename(filename)
    return output.replace('_', ' ').title()


@APP.template_filter('entity_url')
def template_filter_entity_url(entity_id):
    """
    Convert Item of Property string to Wikidata URL
    Args:
        entity_id (str): Item ('Q1234') or Property ('P1234') identifier

    Returns:
        str: http url destination for the entity
    """
    valid_string = get_qid_from_string(entity_id)
    if valid_string:
        return ITEM_URL_PATTERN.replace('$1', valid_string)
    valid_string = get_pid_from_string(entity_id)
    if valid_string:
        return PROPERTY_URL_PATTERN.replace('$1', valid_string)
    return '#'
