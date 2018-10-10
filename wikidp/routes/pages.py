from wikidp import APP
from flask import render_template, request, redirect
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

@APP.route("/q<id>")
@APP.route("/Q<id>")
def route_selected_item(id):
    """If the item ID is already known, the user can enter in the url"""
    return redirect('/Q'+id+'/preview')

@APP.route("/<qid>/preview")
def route_item_preview(qid):
    """If the item ID is already known, the user can enter in the url"""
    selected_item, options, schemas = pages_controller.get_item_context(qid)
    return render_template('preview-item.html', selected=selected_item, options=options, schemas=schemas, page='preview')

@APP.route("/<qid>/contribute")
def route_item_contribute(qid):
    """Handles a user's contributed statements."""
    selected_item, options, schemas = pages_controller.get_item_context(qid)
    return render_template('contribute.html', selected=selected_item, options=options, schemas=schemas, page='contribute')

@APP.route("/<qid>/checklist/<path:schema>")
def route_item_checklist_by_schema(qid, schema):
    """ """
    properties = pages_controller.get_checklist_context(qid, schema)
    return render_template('checklist_items.html', properties=properties)
