from wikidp import APP
from flask import render_template, request, redirect, abort
from wikidp.controllers import pages as pages_controller

@APP.route("/")
def route_page_welcome():
    """Landing Page for first time"""
    return render_template('welcome.html')

@APP.route("/about")
def route_page_about():
    """Rendering the about page"""
    return render_template('about.html')

@APP.route("/reports")
def route_page_reports():
    """Rendering the reports page"""
    return render_template('reports.html')

@APP.route("/browse")
def route_page_browse():
    """Displays a list of extensions and media types."""
    formats = pages_controller.get_browse_context()
    return render_template('browse.html', formats=formats)

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
    try:
        selected_item, options, schemas = pages_controller.get_item_context(qid)
        return render_template('preview-item.html', selected=selected_item, options=options, schemas=schemas, page='preview')
    except:
        return abort(404)

@APP.route("/<item:qid>/contribute")
def route_item_contribute(qid):
    """Handles a user's contributed statements."""
    try:
        selected_item, options, schemas = pages_controller.get_item_context(qid)
        return render_template('contribute.html', selected=selected_item, options=options, schemas=schemas, page='contribute')
    except:
        return abort(404)

@APP.route("/<item:qid>/checklist/<path:schema>")
def route_item_checklist_by_schema(qid, schema):
    """ """
    properties = pages_controller.get_checklist_context(qid, schema)
    return render_template('checklist_items.html', properties=properties)

@APP.errorhandler(400)
@APP.errorhandler(404)
def route_page_error__not_found(e):
    return render_template('error.html', message="Page Not Found"), 404

@APP.errorhandler(403)
def route_page_error__unauthorized(e):
    return render_template('error.html', message="You are not authorized to view this page."), 403

@APP.errorhandler(500)
@APP.errorhandler(Exception)
def route_page_error__internal(e):
    return render_template('error.html', message="Internal Error. Please Help us by reporting this to our admin team! Thank you."), 500
