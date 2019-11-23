"""Module to hold Web App page routing and parameter handling."""
import logging

from flask import (
    abort,
    redirect,
    render_template,
    send_from_directory,
)

from wikidp.config import APP
from wikidp.const import DEFAULT_UI_LANGUAGES
from wikidp.controllers.pages import (
    get_checklist_context,
    get_item_context,
)


@APP.route("/")
def route_page_welcome():
    """Landing Page for first time"""
    return render_template('welcome.html')


@APP.route('/favicon.ico')
def route_favicon():
    """Serve the favicon file."""
    return send_from_directory(APP.config['STATIC_DIR'], 'img/favicon.ico',
                               mimetype='image/vnd.microsoft.icon')


@APP.route("/about")
def route_page_about():
    """Rendering the about page"""
    return render_template('about.html')


@APP.route("/reports")
def route_page_reports():
    """Rendering the reports page"""
    return render_template('reports.html')


@APP.route("/unauthorized")
def route_page_unauthorized():
    """Displays a 403 error page."""
    return abort(403)


@APP.route("/error")
def route_page_error():
    """Displays a 500 error page."""
    return abort(500)


@APP.route("/<item:qid>")
def route_page_selected_item(qid):
    """If the item ID is already known, the user can enter in the url"""
    return redirect('/'+qid+'/preview')


@APP.route("/<item:qid>/preview")
def route_item_preview(qid):
    """If the item ID is already known, the user can enter in the url"""
    selected_item, options, schemas = get_item_context(qid, with_claims=True)
    if selected_item:
        return render_template('item_preview.html', item=selected_item,
                               options=options, schemas=schemas, languages=DEFAULT_UI_LANGUAGES,
                               page='preview')
    return abort(404)


@APP.route("/<item:qid>/contribute")
def route_item_contribute(qid):
    """Handles a user's contributed statements."""
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
    logging.debug('Not Found: %s', str(excep))
    return render_template('error.html', message="Page Not Found"), 404


@APP.errorhandler(403)
def route_page_error_unauthorized(excep):
    """Handle 403 authorisation issues."""
    logging.debug('Unauthorized: %s', str(excep))
    return render_template('error.html', message="You are not authorized to view this page."), 403


@APP.errorhandler(500)
@APP.errorhandler(Exception)
def route_page_error__internal_error(excep):
    """Handle general server errors."""
    logging.debug('Internal Error: %s', str(excep))
    message = "Internal Error. Please Help us by reporting this to our admin team! Thank you."
    return render_template('error.html', message=message), 500
