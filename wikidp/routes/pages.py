"""Module to hold Web App page routing and parameter handling."""
import logging

from flask import (
    abort,
    jsonify,
    redirect,
    render_template,
    send_from_directory,
)

from wikidataintegrator import wdi_core

from wikidp.config import APP
from wikidp.routes.oauth import identify_user, get_wdi_login
from wikidp.const import DEFAULT_UI_LANGUAGES
from wikidp.controllers.pages import (
    get_checklist_context,
    get_item_context,
)

@APP.route("/oauth-write-test")
def write():
    """Test function to ensure OAuth write is working properly."""
    # One-off test to ensure pipes are running, add an alias to WikiDP item
    identity = identify_user()
    for key in identity.keys():
        logging.info('KEY: %s VALUE: %s', key, identity.get(key))
    item = wdi_core.WDItemEngine(wd_item_id="Q51139559")
    item.set_aliases(['WikiDP Application'], append=True)
    assert item.get_label() == "Wikidata for Digital Preservation" # verify api works
    wdi_login = get_wdi_login()
    assert wdi_login.get_edit_token()  # verify edit token exists, this is what WDI calls
    assert "user" in identity.get('groups')  # verify user in user group
    assert "autoconfirmed" in identity.get('groups')  # verify user in user group
    assert "edit" in identity.get('rights')  # verify user in user group
    assert "editpage" in identity.get('grants')  # verify user in user group
    updated = item.write(wdi_login)  # fails due to no permissions
    return jsonify(updated)

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
