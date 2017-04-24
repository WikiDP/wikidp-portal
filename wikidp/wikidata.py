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
"""Some basic Wikidata examples using WikidataIntegrator"""
from wikidataintegrator import wdi_core, wdi_login
from wikidp import APP
from wikidp.queries import QUERIES

def test_query():
    login_instance = wdi_login.WDLogin(user=APP.config.WIKIDATA_USER_NAME, pwd=APP.config.WIKIDATA_PASSWORD)
    results = wdi_core.WDItemEngine.execute_sparql_query(QUERIES['list-formats'].replace('\n', ''))
    return results
