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
from wikidp import APP
from wikidp.utils import remove_extension_from_filename

@APP.template_filter('file_to_label')
def template_filter_file_to_label(filename):
    output = remove_extension_from_filename(filename)
    return output.replace('_', ' ').title()
