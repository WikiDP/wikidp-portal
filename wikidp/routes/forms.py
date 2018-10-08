from wikidp import APP
from flask import request, redirect

@APP.route("/preview", methods=['POST'])
def route_form_preview_item():
    """Show a preview of a selected search result."""
    return redirect('/'+request.form['qid']+'/preview'+'?options='+request.form['optionList'])

@APP.route("/contribute", methods=['POST'])
def route_form_contribute_item():
    """Processes contribute page into a state-saving url."""
    return redirect('/'+request.form['qid']+'/contribute?qid='+request.form['qid']+'&options='+request.form['optionList'])
