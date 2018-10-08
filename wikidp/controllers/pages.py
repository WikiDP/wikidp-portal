from wikidp import APP
from wikidp.const import ConfKey
from wikidp.model import FileFormat
from flask import request, json
import wikidp.DisplayFunctions as DF


def get_browse_context():
    context = FileFormat.list_formats(lang = APP.config[ConfKey.WIKIBASE_LANGUAGE])
    return context

def get_item_context(qid):
    selected_item = DF.item_detail_parse(qid)
    options = request.args.get('options', default = 0, type = str)
    if type(options) is str:
        options = json.loads(options)
    else:
        basic_details = DF.qid_to_basic_details(qid)
        options = [[qid, basic_details['label'], basic_details['description']]]
    return selected_item, options
