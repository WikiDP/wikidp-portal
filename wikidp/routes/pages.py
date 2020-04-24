"""Module to hold Web App page routing and parameter handling."""
import logging
import os

from flask import (
    abort,
    redirect,
    render_template,
    send_from_directory,
)
from flask_mwoauth import MWOAuth

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

MWOAUTH = MWOAuth(consumer_key=ORG_TOKEN, consumer_secret=SECRET_TOKEN,
                  user_agent=USER_AGENT, default_return_to="profile")
APP.register_blueprint(MWOAUTH.bp)

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

@APP.route("/profile")
def profile():
    """Flask OAuth login."""
    logging.debug("getting user")
    username = MWOAUTH.get_current_user(True)
    identity = None
    if username is not None:
        identity = MWOAUTH.get_user_identity(False)
    return render_template('profile.html', username=username, identity=identity)

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
                               options=options, schemas=schemas, languages=DEFAULT_UI_LANGUAGES,
                               page='preview')
    return abort(404)


@APP.route("/<item:qid>/contribute")
def route_item_contribute(qid):
    """Handle a user's contributed statements."""
    selected_item, options, schemas = get_item_context(qid, with_claims=False)
    if selected_item:
        return render_template('item_contribute.html', item=selected_item,
                               options=options, schemas=schemas, languages=DEFAULT_UI_LANGUAGES,
                               page='contribute')
    return abort(404)


@APP.route("/<item:qid>/checklist/<path:schema>")
def route_item_checklist_by_schema(qid, schema):
    """Render the correct item checklist depending on schema."""
    properties = get_checklist_context(qid, schema)
    return render_template('snippets/property_checklist.html', properties=properties)

@APP.errorhandler(400)
@APP.errorhandler(404)
def route_page_error__not_found(excep):
    """Handle 404 resource not found problems."""
    _log_error_message('Not Found: %s', excep)
    return render_template('error.html', message="Page Not Found"), 404

@APP.errorhandler(403)
def route_page_error__forbidden(excep):
    """Handle HTTP 403, Forbidden."""
    _log_error_message('Forbidden: %s', excep)
    return render_template('error.html', message="You are not authorized to view this page."), 403

@APP.errorhandler(500)
@APP.errorhandler(Exception)
def route_page_error__internal_error(excep):
    """Handle general server errors."""
    _log_error_message('Internal Server Error: %s', excep)
    message = "Internal Error. Please Help us by reporting this to our admin team! Thank you."
    return render_template('error.html', message=message), 500


def _log_error_message(code_type, excep):
    logging.debug(code_type, str(excep))
