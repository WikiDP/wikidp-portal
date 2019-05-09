""" Collection of sparql queries and related functions turned into python functions """

PROPERTY_QUERY = """
    SELECT  (STRAFTER(STR(?property), 'entity/') as ?id) ?property ?propertyType ?propertyLabel 
    ?propertyDescription ?propertyAltLabel (STRAFTER(STR(?propertyType), '#') as ?value_type) ?formatter_url
    WHERE {
    VALUES (?property) { $values }
    ?property wikibase:propertyType ?propertyType .
    OPTIONAL {
      ?property wdt:P1630 ?formatter_url.
    }
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    ORDER BY ASC(xsd:integer(STRAFTER(STR(?property), 'P')))
"""

ALL_QUALIFIER_PROPERTIES = """
    SELECT (STRAFTER(STR(?property), 'entity/') as ?id) ?property ?propertyType ?propertyLabel 
    ?propertyDescription ?propertyAltLabel (STRAFTER(STR(?propertyType), '#') as ?value_type)
    WHERE {
      ?property wikibase:propertyType ?propertyType .
      ?property wdt:P31 wd:Q15720608 .
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    ORDER BY ASC(xsd:integer(STRAFTER(STR(?property), 'P')))
"""

PROPERTY_ALLOWED_QUALIFIERS = """
    SELECT (STRAFTER(STR(?property), 'entity/') as ?id) ?property ?propertyType ?propertyLabel  ?propertyAltLabel
    (?propertyLabel as ?label) ?propertyDescription (?propertyDescription as ?description) 
    (STRAFTER(STR(?propertyType), '#') as ?value_type)
    WHERE {
        VALUES (?main_property) { $values }
        ?main_property p:P2302 ?constraint.
        ?constraint ps:P2302 wd:Q21510851 .
        ?constraint pq:P2306 ?property.
        ?property wikibase:propertyType ?propertyType .
        SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
"""