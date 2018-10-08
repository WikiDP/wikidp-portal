from wikidp import APP
from flask import redirect, render_template, request
from wikidp.controllers import search as search_controller

@APP.route("/search", methods=['POST'])
def route_process_site_search():
    """Processes search request into a state-saving url."""
    return redirect('/search?string='+request.form['userInput'].strip())

@APP.route("/search")
def route_site_search():
    """
    Displays the most likely results of a users search
    if only one result returned, the user is automatic redirected to preview that item
    """
    search_string = request.args.get('string', default = 0, type = str)
    context = search_controller.get_search_result_context(search_string)
    if len(context) == 1:
        return redirect ('/'+context[0]['id'])
    return render_template('search_results.html', options=context)

@APP.route("/search/puid/<string:puid>")
def route_search_by_puid(puid):
    """Displays a list of extensions and media types."""
    new_puid, results = search_controller.get_search_by_puid_context(puid)
    return render_template('puid_results.html', results=results, puid=new_puid)
