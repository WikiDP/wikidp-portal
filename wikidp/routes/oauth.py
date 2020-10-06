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
"""All things OAuth."""
import os
import jsonpickle

from flask import Blueprint, session, redirect, request
from mwoauth import AccessToken
from wikidataintegrator import wdi_login

# OAuth stuff
ORG_TOKEN = os.environ.get('CONSUMER_TOKEN', '')
SECRET_TOKEN = os.environ.get('SECRET_TOKEN', '')
CB_URL = os.environ.get('OAUTH_CB', 'oob')
SESSKY_AUTH='authOBJ'
HOST=os.environ.get('HOST', 'oob')

USER_AGENT = 'wikidp-portal/0.0 (https://wikidp.org/portal/; admin@wikidp.org)'

class WDPOAuth:
    def __init__(self,
                 consumer_key=ORG_TOKEN,
                 consumer_secret=SECRET_TOKEN,
                 cb_url=CB_URL,
                 user_agent=USER_AGENT,
                 **kwargs):

        self.bp = Blueprint('wdpoauth', __name__, **kwargs)
        self.consumer_key=consumer_key
        self.consumer_secret=consumer_secret
        self.cb_url=cb_url
        self.user_agent=user_agent

        @self.bp.route("/mwoauth/initiate/")
        def mwoauth_initiate():
            authentication = wdi_login.WDLogin(self.consumer_key,
                                               self.consumer_secret,
                                               self.cb_url,
                                               self.user_agent)
            session[SESSKY_AUTH] = jsonpickle.encode(authentication)
            return redirect(authentication.redirect)

        @self.bp.route("/mwoauth/callback/")
        def mwoauth_callback():
            authentication = jsonpickle.decode(session[SESSKY_AUTH])
            authentication.continue_oauth(request.url)
            access_token = AccessToken(authentication.s.auth.client.resource_owner_key,
                                       authentication.s.auth.client.resource_owner_secret)
            identity = authentication.handshaker.identify(access_token)
            session["username"]=identity['username']
            session["userid"]=identity['sub']
            # return jsonify(body)
