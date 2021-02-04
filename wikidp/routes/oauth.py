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
"""Flask MWOAuth and WikiDataIntegrator come together."""
import logging
import os

import json
import jsonpickle

from mwoauth import ConsumerToken, AccessToken, identify

from flask import (
    jsonify,
    render_template,
    request,
    session,
)

from wikidataintegrator import wdi_login

from wikidp.config import APP

# OAuth stuff
CONSUMER_TOKEN = ConsumerToken(os.environ.get('CONSUMER_TOKEN', ''),
                               os.environ.get('SECRET_TOKEN', ''))
OAUTH_MEDIAWIKI_URL = 'https://www.wikidata.org/w/index.php'
WIKIDATA_API = 'https://www.wikidata.org/w/api.php'
USER_AGENT = 'wikidp-portal/0.0 (https://www.wikidp.org/; admin@wikidp.org)'

@APP.route("/", methods=['POST', 'GET'])
def route_page_welcome():
    """Landing Page for first time."""
    if request.method == 'POST':
        body = json.loads(request.get_data())
        # parse the url from wikidata for the oauth token and secret
        if 'url' in body.keys():
            if is_authenticated():
                return jsonify(body)

            wdi_login_obj = get_wdi_login()
            wdi_login_obj.continue_oauth(oauth_callback_data=body['url'].encode("utf-8"))
            store_wdi_login(wdi_login_obj)
            login()
            return jsonify(body)
    return render_template('welcome.html')

@APP.route("/profile", methods=['POST', 'GET'])
def profile():
    """Flask OAuth login."""
    logging.info("Checking user profile")
    if request.method == 'POST':
        logging.info("POST so getting data")
        body = json.loads(request.get_data())
        if 'initiate' in body.keys():
            wdi_login_obj = wdi_login.WDLogin(consumer_key=CONSUMER_TOKEN.key,
                                              consumer_secret=CONSUMER_TOKEN.secret,
                                              callback_url='oob',
                                              mediawiki_api_url=WIKIDATA_API,
                                              user_agent=USER_AGENT)
            store_wdi_login(wdi_login_obj)
            response_data = {
                'wikimediaURL': wdi_login_obj.redirect
            }
            return jsonify(response_data)
    elif request.method == 'GET' and request.args.get('logout'):
        logout()

    return render_template('profile.html', username=session.get('username', ''))

@APP.route("/auth")
def authenication():
    """
    Return a simple JSON structure confirming user authenication.

    Simple GET service that returns a tiny dictionary informing the caller
    as to whether the current session user is authenticated, accompanied by their
    user name if they are.
    """
    is_user_authenticated = is_authenticated()
    response_data = {
        'auth' : is_user_authenticated,
        'username' : session.get('username', '')
    }
    return jsonify(response_data)

def identify_user():
    """Return the user identity object obtained from the session WDI login."""
    # Get the WDI login object
    wdi_login_obj = get_wdi_login()
    access_token = AccessToken(
        wdi_login_obj.s.auth.client.resource_owner_key,
        wdi_login_obj.s.auth.client.resource_owner_secret
    )
    return identify(OAUTH_MEDIAWIKI_URL,
                    CONSUMER_TOKEN, access_token)

def is_authenticated():
    """Return true if a user is authenticated, otherwise false."""
    if session.get('username'):
        return True
    return False

def store_wdi_login(wdi_login_obj):
    """Return the WDI login object from session."""
    session['wdilogin'] = jsonpickle.encode(wdi_login_obj)

def get_wdi_login():
    """Return the WDI login object from session."""
    return jsonpickle.decode(session['wdilogin'])

def login():
    """Get the current user and store the username in the session."""
    identity = identify_user()
    session["username"] = identity['username']

def logout():
    """Remove the current user from the session."""
    session.pop('username')
