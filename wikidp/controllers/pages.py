from wikidp import APP
from wikidp.const import ConfKey
from wikidp.model import FileFormat
from wikidp.controllers.api import get_property_checklist_from_schema
from flask import request, json
import wikidp.DisplayFunctions as DF
from wikidp.utils import get_directory_filenames_with_subdirectories
SCHEMA_DIRECTORY_PATH = 'wikidp/schemas/'

def get_browse_context():
    context = FileFormat.list_formats(lang=APP.config[ConfKey.WIKIBASE_LANGUAGE])
    return context

def get_item_context(qid):
    selected_item = DF.item_detail_parse(qid)
    if selected_item is False:
        return False
    options = request.args.get('options', default=0, type=str)
    if type(options) is str:
        options = json.loads(options)
    else:
        basic_details = DF.qid_to_basic_details(qid)
        options = [[qid, basic_details['label'], basic_details['description']]]
    schemas = get_schema_list()
    return selected_item, options, schemas

def get_checklist_context(qid, schema):
    checklist = get_property_checklist_from_schema(schema, source='server')
    if checklist == []:
        return []
    selected_item = DF.item_detail_parse(qid)
    counts = selected_item['prop-counts']
    output = [{
                "pid": prop['id']['value'],
                "label": prop['propertyLabel']['value'],
                "description": prop['propertyDescription']['value'],
                "type": prop["valueType"]['value'],
                "count": counts[prop['id']['value']] if prop['id']['value'] in counts else 0
                } for prop in checklist]
    return output

def get_schema_list():
    raw_list = get_directory_filenames_with_subdirectories(SCHEMA_DIRECTORY_PATH)
    return raw_list
