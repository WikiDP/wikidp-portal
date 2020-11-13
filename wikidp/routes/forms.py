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
# This is a python __init__ script to create the app and import the
# main package contents
"""Module for application form routes."""
from flask import (
    redirect,
    request,
)
import json

from wikidp.config import APP


def _get_page_redirect(action):
    """
    Get the Redirect with Formatted Deep-linking.

    Args:
        action (Literal['contribute', 'preview']):

    Returns (Response):

    """
    qid = request.form['qid']
    options = ",".join(json.loads(request.form['optionList']))
    return redirect(f'/{qid}/{action}?qid={qid}&options={options}')


@APP.route("/preview", methods=['POST'])
def route_form_preview_item():
    """
    Show a preview of a selected search result.

    Returns (Response):

    """
    return _get_page_redirect('preview')


@APP.route("/contribute", methods=['POST'])
def route_form_contribute_item():
    """
    Process contribute page into a state-saving url.

    Returns (Response):

    """
    return _get_page_redirect('contribute')
