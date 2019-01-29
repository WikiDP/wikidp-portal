from flask import (
    redirect,
    request,
)
from wikidp.config import APP


@APP.route("/preview", methods=['POST'])
def route_form_preview_item():
    """Show a preview of a selected search result."""
    return redirect('/'+request.form['qid']+'/preview'+'?options='+request.form['optionList'])


@APP.route("/contribute", methods=['POST'])
def route_form_contribute_item():
    """Processes contribute page into a state-saving url."""
    qid = request.form['qid']
    return redirect('/{}/contribute?qid={}&options={}'.format(qid, qid, request.form['optionList']))
