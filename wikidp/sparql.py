""" Collection of sparql queries and related functions turned into python functions """
PROPERTY_QUERY = """
            SELECT  (STRAFTER(STR(?property), 'entity/') as ?id) ?property ?propertyType ?propertyLabel 
            ?propertyDescription ?propertyAltLabel (STRAFTER(STR(?propertyType), '#') as ?valueType) ?formatter_url
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
