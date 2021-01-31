"""Methods for user authentication and authorization."""
from flask import session
import jsonpickle
from mwoauth import (
    ConsumerToken,
    AccessToken,
    identify,
)
from wikidataintegrator.wdi_login import WDLogin

from wikidp.config import APP
from wikidp.const import (
    ConfKey,
    OAUTH_MEDIAWIKI_URI,
)

MEDIAWIKI_API_URL = APP.config[ConfKey.MEDIAWIKI_API_URL]
WIKIDP_CONSUMER_KEY = APP.config[ConfKey.WIKIDP_CONSUMER_KEY]
WIKIDP_CONSUMER_SECRET = APP.config[ConfKey.WIKIDP_CONSUMER_SECRET]
WIKIDP_CONSUMER_TOKEN = ConsumerToken(WIKIDP_CONSUMER_KEY,
                                      WIKIDP_CONSUMER_SECRET)
USER_AGENT = APP.config[ConfKey.USER_AGENT]


def identify_user():
    """Return the user identity object obtained from the session WDI login."""
    # Get the WDI login object
    wdi_login_obj = get_wdi_login()
    access_token = AccessToken(
        wdi_login_obj.s.auth.client.resource_owner_key,
        wdi_login_obj.s.auth.client.resource_owner_secret
    )
    return identify(OAUTH_MEDIAWIKI_URI, WIKIDP_CONSUMER_TOKEN, access_token)


def is_authenticated():
    """Return true if a user is authenticated, otherwise false."""
    if session.get('username'):
        return True
    return False


def store_wdi_login(wdi_login_obj):
    """
    Store the WDI login object into the session.

    Args:
        wdi_login_obj (WDLogin):

    Returns:

    """
    session['wdilogin'] = jsonpickle.encode(wdi_login_obj)


def get_wdi_login():
    """
    Get the WDI login object from session.

    Args:

    Returns (WDLogin):

    """
    return jsonpickle.decode(session['wdilogin'])


def build_wdi_login():
    """
    Build the WDI Login Object with Oauth Consumer.

    Returns (WDLogin):

    """
    return WDLogin(consumer_key=WIKIDP_CONSUMER_TOKEN.key,
                   consumer_secret=WIKIDP_CONSUMER_TOKEN.secret,
                   callback_url='oob',
                   mediawiki_api_url=MEDIAWIKI_API_URL,
                   user_agent=USER_AGENT)


def login():
    """Get the current user and store the username in the session."""
    identity = identify_user()
    session["username"] = identity['username']


def logout():
    """Remove the current user from the session."""
    session.pop('username')
