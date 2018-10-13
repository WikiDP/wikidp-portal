import logging
import re
from wikidp import APP
from wikidp.const import ConfKey
from wikidp.model import PuidSearchResult

import wikidp.DisplayFunctions as DF
def get_search_result_context(search_string):
    context = []
    # Check if searching with PUID
    if re.search("[x-]?fmt/\d+", search_string) != None:
        result = PuidSearchResult.search_puid( search_string, lang = APP.config[ConfKey.WIKIBASE_LANGUAGE])
        for res in result:
            item = DF.qid_to_basic_details(res.format)
            context.append({
                'id': res.format,
                'label': res.label,
                'description': item['description']
            })
    context += DF.search_result_list(search_string)
    return context

def get_search_by_puid_context(puid):
    new_puid = puid.replace('_', '/')
    logging.debug("Searching for PUID: %s", new_puid)
    results = PuidSearchResult.search_puid(new_puid, lang = APP.config[ConfKey.WIKIBASE_LANGUAGE])
    return new_puid, results
