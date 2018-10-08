#!/usr/bin/python
# coding=UTF-8
#
# WikiDP Wikidata Portal
# Copyright (C) 2017
# All rights reserved.
#
# This code is distributed under the terms of the GNU General Public
# License, Version 3. See the text file "COPYING" for further details
# about the terms of this license.
#
"""Controller functions for writing to wikidata."""

import pywikibot
SANDBOX_API_URL = 'https://test.wikidata.org/w/'
SANDBOX_SPARQL_URL = 'https://test.wikidata.org/proxy/wdqs/bigdata/namespace/wdq/'
SITE = pywikibot.Site("test", "wikidata")
REPO = SITE.data_repository()

def write_claim(qid, property, value, meta=False):
    '''Function for writing a claim to WikiData

    Args:
        qid (str): Wikidata Item Identifier [ex. 'Q1234']
        property (str): Wikidata Property Identifier [ex. 'P1234']
        value (str): Value matching accepted property type (could be other datatypes)
        meta (dict, optional): Contains information about qualifiers/references/summaries
    Returns:
        bool: True if successful, False otherwise
    '''
    try:
        # TODO: Convert to writes to any item by uncommenting line 34
        item = pywikibot.ItemPage(REPO, u"Q175461") # WIKIDATA TESTING ITEM
        # item = pywikibot.ItemPage(REPO, qid)
        claim = pywikibot.Claim(REPO, property)
        target = pywikibot.ItemPage(REPO, value)
        claim.setTarget(target)
        item.addClaim(claim, summary=u'Adding claim')
        return True
    except Exception as e:
        return False
