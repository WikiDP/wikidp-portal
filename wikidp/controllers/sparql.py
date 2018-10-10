""" Collection of sparql queries and related functions turned into python functions """

from wikidataintegrator import wdi_core

def convert_list_to_value_string(lst):
    """
        Arg: lst, ex: ['P31', 'P5', 'P123']
        Returns: "(wd:P31)(wd:P5)(wd:P123)"
    """
    return '(wd:{0})'.format(')(wd:'.join(map(str, lst)))

def get_property_details_by_pid_list(pid_list):
    values = convert_list_to_value_string(pid_list)
    query_string = """
            SELECT  (STRAFTER(STR(?property), 'entity/') as ?id) ?property ?propertyType ?propertyLabel ?propertyDescription ?propertyAltLabel  (STRAFTER(STR(?propertyType), '#') as ?valueType)
            WHERE {{
            VALUES (?property) {{ {values} }}
            ?property wikibase:propertyType ?propertyType .
              SERVICE wikibase:label {{ bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }}
            }}
            ORDER BY ASC(xsd:integer(STRAFTER(STR(?property), 'P')))
        """.format(values=values)
    query_string = " ".join(query_string.split())
    result = wdi_core.WDItemEngine.execute_sparql_query(query_string)
    return result
