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

USER_AGENT = 'wikidp-portal/0.0 (https://wikidp.org/portal/; admin@wikidp.org)'

@APP.route("/profile", methods=['POST', 'GET'])
def profile():
    """Flask OAuth login."""
    if request.method == 'POST':
        body = json.loads(request.get_data())
        if 'initiate' in body.keys():
            authentication = wdi_login.WDLogin(consumer_key=CONSUMER_TOKEN.key,
                                               consumer_secret=CONSUMER_TOKEN.secret,
                                               callback_url=request.url_root + "profile",
                                               user_agent=USER_AGENT)
            session['authOBJ'] = jsonpickle.encode(authentication)
            response_data = {
                'wikimediaURL': authentication.redirect
            }
            return jsonify(response_data)

        # parse the url from wikidata for the oauth token and secret
        if 'url' in body.keys():
            if session.get("username"):
                return jsonify(body)

            authentication = jsonpickle.decode(session['authOBJ'])
            authentication.continue_oauth(oauth_callback_data=body['url'].encode("utf-8"))
            session['authOBJ'] = jsonpickle.encode(authentication)
            access_token = AccessToken(
                authentication.s.auth.client.resource_owner_key,
                authentication.s.auth.client.resource_owner_secret
            )
            identity = identify("https://www.mediawiki.org/w/index.php",
                                CONSUMER_TOKEN, access_token)
            session["username"]=identity['username']
            session["userid"]=identity['sub']
            return jsonify(body)
    elif request.method == 'GET' and request.args.get('logout'):
        session.pop('username')

    return render_template('profile.html', username=session.get('username', ''))

@APP.route("/auth")
def authenication():
    response_data = {
        'auth' : False
    }
    if session.get('username'):
        response_data = {
            'auth' : True,
            'username' : session['username']
        }
    return jsonify(response_data)
