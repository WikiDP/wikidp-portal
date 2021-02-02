#!/usr/bin/python
# coding=UTF-8
#
# WikiDP Wikidata Portal
# Copyright (C) 2021
# All rights reserved.
#
# This code is distributed under the terms of the GNU General Public
# License, Version 3. See the text file "COPYING" for further details
# about the terms of this license.
#
"""Flask MWOAuth and WikiDataIntegrator come together."""
import json
import logging

from flask import (
    jsonify,
    redirect,
    render_template,
    request,
    session,
)
from wikidataintegrator.wdi_core import WDItemEngine

from wikidp.config import APP
from wikidp.controllers.auth import (
    build_wdi_login,
    get_wdi_login,
    identify_user,
    is_authenticated,
    login,
    logout,
    store_wdi_login,
)


@APP.route("/", methods=['POST'])
def route_page_login():
    """
    Handle the user login via Oauth.

    Returns (Response): JSON Response

    """
    body = json.loads(request.get_data())
    if 'url' not in body:
        return redirect('/')

    # parse the url from wikidata for the oauth token and secret
    if is_authenticated():
        return jsonify(body)
    wdi_login_obj = get_wdi_login()
    callback = body['url'].encode("utf-8")
    wdi_login_obj.continue_oauth(oauth_callback_data=callback)
    store_wdi_login(wdi_login_obj)
    login()
    return jsonify(body)


@APP.route("/profile", methods=['POST', 'GET'])
def profile():
    """Flask OAuth login."""
    logging.info("Checking user profile")
    if request.method == 'POST':
        logging.info("POST so getting data")
        body = json.loads(request.get_data())
        if 'initiate' in body.keys():
            wdi_login_obj = build_wdi_login()
            store_wdi_login(wdi_login_obj)
            response_data = {
                'wikimediaURL': wdi_login_obj.redirect
            }
            return jsonify(response_data)
    elif request.method == 'GET' and request.args.get('logout'):
        logout()

    return render_template('profile.html', username=session.get('username', ''))


@APP.route("/auth")
def route_authentication():
    """
    Get a simple JSON structure confirming user authentication.

    Notes:
        - Simple GET service that returns a tiny dictionary informing the
        caller as to whether the current session user is authenticated,
        accompanied by their user name if they are.

    Returns (Response):

    """
    is_user_authenticated = is_authenticated()
    response_data = {
        'auth': is_user_authenticated,
        'username': session.get('username', ''),
    }
    return jsonify(response_data)


@APP.route("/oauth-write-test")
def _temp_route_oauth_write_test():
    # One-off test to ensure pipes are running, add an alias to WikiDP item
    identity = identify_user()
    for key in identity.keys():
        logging.info('KEY: %s VALUE: %s', key, identity.get(key))
    item = WDItemEngine(wd_item_id="Q51139559")
    item.set_aliases(['WikiDP Application'], append=True)
    # verify the api is working by getting this item
    assert item.get_label() == "Wikidata for Digital Preservation"
    wdi_login = get_wdi_login()
    # verify edit token exists, this is what WDI calls
    assert wdi_login.get_edit_token()
    assert "user" in identity.get('groups')  # verify user in user group
    # verify user in user group
    assert "autoconfirmed" in identity.get('groups')
    assert "edit" in identity.get('rights')  # verify user in user group
    assert "editpage" in identity.get('grants')  # verify user in user group
    updated = item.write(wdi_login)  # fails due to no permissions
    return jsonify(updated)
