"""Module to hold Web App page routing and parameter handling."""
import logging
import os

import json
import jsonpickle

from mwoauth import AccessToken

from flask import (
    abort,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    send_from_directory,
)

from wikidataintegrator import wdi_login

from wikidp.config import APP
from wikidp.const import DEFAULT_UI_LANGUAGES
from wikidp.controllers.pages import (
    get_checklist_context,
    get_item_context,
)

# OAuth stuff
ORG_TOKEN = os.environ.get('CONSUMER_TOKEN', '')
SECRET_TOKEN = os.environ.get('SECRET_TOKEN', '')

USER_AGENT = 'wikidp-portal/0.0 (https://wikidp.org/portal/; admin@wikidp.org)'


# MWOAUTH = MWOAuth(consumer_key=ORG_TOKEN, consumer_secret=SECRET_TOKEN,
#                   user_agent=USER_AGENT, default_return_to="/profile")
# APP.register_blueprint(MWOAUTH.bp)
@APP.route("/")
def route_page_welcome():
    """Landing Page for first time."""
    return render_template('welcome.html')


@APP.route('/favicon.ico')
def route_favicon():
    """Serve the favicon file."""
    return send_from_directory(APP.config['STATIC_DIR'], 'img/favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@APP.route("/about")
def route_page_about():
    """Render the about page."""
    return render_template('about.html')


@APP.route("/reports")
def route_page_reports():
    """Render the reports page."""
    return render_template('reports.html')


@APP.route("/auth")
def authenication():
    """Return the authorisation status as JSON."""
    response_data = {
        'auth' : False
    }
    if session.get('username'):
        response_data = {
            'auth' : True,
            'username' : session['username']
        }
    return jsonify(response_data)


@APP.route("/logout")
def logout():
    """Clear out session variables and redirect to profile display."""
    session.clear()
    return redirect("profile", code=303)


@APP.route("/profile", methods=['POST', 'GET'])
def profile():
    """Flask OAuth login."""
    if request.method == 'POST':
        body = json.loads(request.get_data())
        if 'initiate' in body.keys():
            authentication = wdi_login.WDLogin(consumer_key=ORG_TOKEN,
                                               consumer_secret=SECRET_TOKEN,
                                               callback_url=request.url_root + "profile",
                                               user_agent=USER_AGENT)
            session['authOBJ'] = jsonpickle.encode(authentication)
            response_data = {
                'wikimediaURL': authentication.redirect
            }
            return jsonify(response_data)

        # parse the url from wikidata for the oauth token and secret
        if 'url' in body.keys():
            authentication = jsonpickle.decode(session['authOBJ'])
            authentication.continue_oauth(oauth_callback_data=body['url'].encode("utf-8"))
            access_token = AccessToken(authentication.s.auth.client.resource_owner_key,
                                       authentication.s.auth.client.resource_owner_secret)
            identity = authentication.handshaker.identify(access_token)
            session["username"] = identity['username']
            session["userid"] = identity['sub']
            return jsonify(body)

    return render_template('profile.html', username=session.get('username', None))


@APP.route("/unauthorized")
def route_page_unauthorized():
    """Display a 403 error page."""
    return abort(403)


@APP.route("/error")
def route_page_error():
    """Display a 500 error page."""
    return abort(500)


@APP.route("/<item:qid>")
def route_page_selected_item(qid):
    """If the item ID is already known, the user can enter in the url."""
    return redirect('/'+qid+'/preview')


@APP.route("/<item:qid>/preview")
def route_item_preview(qid):
    """If the item ID is already known, the user can enter in the url."""
    selected_item, options, schemas = get_item_context(qid, with_claims=True)
    if selected_item:
        return render_template('item_preview.html', item=selected_item,
                               options=options, schemas=schemas,
                               languages=DEFAULT_UI_LANGUAGES,
                               page='preview')
    return abort(404)


@APP.route("/<item:qid>/contribute")
def route_item_contribute(qid):
    """Handle a user's contributed statements."""
    selected_item, options, schemas = get_item_context(qid, with_claims=False)
    if selected_item:
        return render_template('item_contribute.html', item=selected_item,
                               options=options, schemas=schemas,
                               languages=DEFAULT_UI_LANGUAGES,
                               page='contribute')
    return abort(404)


@APP.route("/<item:qid>/checklist/<path:schema>")
def route_item_checklist_by_schema(qid, schema):
    """Render the correct item checklist depending on schema."""
    properties = get_checklist_context(qid, schema)
    return render_template('snippets/property_checklist.html',
                           properties=properties)


@APP.errorhandler(400)
@APP.errorhandler(404)
def route_page_error__not_found(excep):
    """Handle 404 resource not found problems."""
    logging.exception('Not Found: %s', excep)
    return render_template('error.html', message="Page Not Found"), 404


@APP.errorhandler(403)
def route_page_error__forbidden(excep):
    """Handle HTTP 403, Forbidden."""
    logging.exception('Forbidden: %s', excep)
    message = "You are not authorized to view this page."
    return render_template('error.html', message=message), 403


@APP.errorhandler(500)
@APP.errorhandler(Exception)
def route_page_error__internal_error(excep):
    """Handle general server errors."""
    logging.exception('Internal Server Error: %s', excep)
    message = "Internal Error. Please Help us by reporting " \
              "this to our admin team! Thank you."
    return render_template('error.html', message=message), 500
