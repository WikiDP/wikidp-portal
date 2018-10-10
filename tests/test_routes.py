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
"""Unit tests for WikiData reads."""
from unittest import TestCase

import pywikibot

from wikidataintegrator import wdi_core
from wikidataintegrator.wdi_core import WDItemEngine

from wikidp.model import FileFormat, PuidSearchResult
SANDBOX_API_URL = 'https://test.wikidata.org/w/'
SANDBOX_SPARQL_URL = 'https://test.wikidata.org/proxy/wdqs/bigdata/namespace/wdq/'
SITE = pywikibot.Site("test", "wikidata")
REPO = SITE.data_repository()

import pytest
from wikidp import APP
from flask import jsonify
import json
# class APITests(TestCase):
#     def test_search_item_by_string(self):
#         """Queries Wikidata for formats and returns a list of FileFormat instances."""
#         results = api.search_item_by_string('grace hopper')
#
#         assert results, \
#         'Format read returned no results'

@pytest.fixture
def client(request):
    test_client = APP.test_client()

    def teardown():
        pass # databases and resourses have to be freed at the end. But so far we don't have anything

    request.addfinalizer(teardown)
    return test_client

def post_json(client, url, json_dict):
    """Send dictionary json_dict as a json to the specified url """
    return client.post(url, data=json.dumps(json_dict), content_type='application/json')

def json_response(response):
    """Decode json from response"""
    return json.loads(response.data.decode('utf8'))

# PAGES TESTS

def test_route_page_welcome(client):
    """Test the client loads the homepage title  """
    response = client.get('/')
    assert response.status_code == 200
    assert b'WikiDP | Home' in response.data

def test_route_page_about(client):
    """Test the client loads the about title  """
    response = client.get('/about')
    assert response.status_code == 200
    assert b'WikiDP | About' in response.data

def test_route_page_reports(client):
    """Test the client loads the reports title  """
    response = client.get('/reports')
    assert response.status_code == 200
    assert b'WikiDP | Reports' in response.data

def test_route_page_browse(client):
    """Test the client loads the browse title  """
    response = client.get('/browse')
    assert response.status_code == 200
    assert b'WikiDP | Browse' in response.data

def test_route_item_preview(client):
    """Test the client loads the preview of sample item  """
    response = client.get('/Q7715973', follow_redirects=True)
    assert response.status_code == 200
    assert b'Q7715973' in response.data

def test_route_item_preview(client):
    """Test the client loads the preview of sample item  """
    response = client.get('/Q7715973/preview')
    assert response.status_code == 200
    assert b'Q7715973' in response.data

def test_route_item_contribute(client):
    """Test the client loads the contribute of sample item  """
    response = client.get('/Q7715973/contribute')
    assert response.status_code == 200
    assert b'Q7715973' in response.data

# TODO: Once a schema is added without a category add a test

def test_route_item_checklist_by_schema__with_category(client):
    response = client.get('/Q7715973/checklist/file_format/file_format_minimal.json')
    assert response.status_code == 200
    assert b'sidebar-property-li' in response.data

def test_route_item_checklist_by_schema__fake_schema(client):
    response = client.get('/Q7715973/checklist/fake_schema.json')
    assert response.status_code == 200
    assert b'no suggested properties in this schema' in response.data

# TODO: FORMS TEST

# SEARCH TESTS
def test_route_site_search__by_label(client):
    """Test the client loads the contribute of sample item  """
    response = client.get('/search?string=debian')
    assert response.status_code == 200
    assert b'Q7715973' in response.data

def test_route_site_search__by_puid(client):
    """Test the client loads the contribute of sample item  """
    response = client.get('/search?string=fmt/354', follow_redirects=True)
    assert response.status_code == 200
    assert b'Q26543628' in response.data

def test_route_search_by_puid(client):
    """Test the client loads the contribute of sample item  """
    response = client.get('/search/puid/fmt_354', follow_redirects=True)
    assert response.status_code == 200
    assert b'Q26543628' in response.data

# API TESTS

def test_route_api_welcome(client):
    """Test the client loads the homepage title  """
    response = client.get('/api/')
    assert response.status_code == 200
    assert b'Welcome to the WikiDP API' in response.data

def test_route_api_search_item_by_string(client):
    response = client.get('/api/search/debian')
    assert response.status_code == 200
    assert len(json_response(response)) > 0

def test_route_api_get_item_label(client):
    response = client.get('/api/Q7715973/label')
    assert response.status_code == 200
    assert json_response(response)['id'] == 'Q7715973'


def test_route_api_get_schema_properties__with_category(client):
    response = client.get('/api/schema/file_format/file_format_minimal.json/properties')
    assert response.status_code == 200
    assert len(json_response(response)) > 0
    assert 'id' in json_response(response)[0]

# TODO: Once a schema is added without a category add a api test

def test_route_api_get_properties_by_schema__with_category(client):
    response = client.get('/api/schema/file_format/file_format_minimal.json/properties')
    assert response.status_code == 200
    assert len(json_response(response)) > 0
    assert 'id' in json_response(response)[0]


def test_route_api_get_properties_by_schema__fake_schema(client):
    response = client.get('/api/schema/fake_schema.json/properties')
    assert response.status_code == 200
    assert len(json_response(response)) == 0
    assert json_response(response) == []

# TODO: Test for route_api_write_claims_to_item
