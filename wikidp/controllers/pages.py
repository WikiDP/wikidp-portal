from flask import (
    json,
    request,
)

from wikidp import APP
from wikidp.const import ConfKey
from wikidp.models import FileFormat
from wikidp.controllers.api import get_property_checklist_from_schema
from wikidp.utils import (
    item_detail_parse,
    get_directory_filenames_with_subdirectories,
    get_item_property_counts,
)

SCHEMA_DIRECTORY_PATH = 'wikidp/schemas/'


def get_browse_context():
    context = FileFormat.list_formats(lang=APP.config[ConfKey.WIKIBASE_LANGUAGE])
    return context


def get_item_context(qid):
    selected_item = item_detail_parse(qid)
    options = None
    schemas = None
    if selected_item:
        options = request.args.get('options', default=0, type=str)
        if type(options) is str:
            options = json.loads(options)
        else:
            options = [[qid, selected_item.get('label'), selected_item.get('description')]]
        schemas = get_schema_list()
    return selected_item, options, schemas


def get_checklist_context(qid, schema):
    checklist = get_property_checklist_from_schema(schema)
    if checklist:
        counts = get_item_property_counts(qid)
        output = [{
                    "pid": prop['id']['value'],
                    "label": prop['propertyLabel']['value'],
                    "description": prop['propertyDescription']['value'],
                    "type": prop["valueType"]['value'],
                    "count": counts.get(prop['id']['value'], 0)
                    } for prop in checklist]
        return output
    return []


def get_schema_list():
    raw_list = get_directory_filenames_with_subdirectories(SCHEMA_DIRECTORY_PATH)
    return raw_list
