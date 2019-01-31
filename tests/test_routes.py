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
"""Client tests for WikiDP Routes."""
import pytest
from flask import json

from tests import settings
from wikidp import APP


@pytest.fixture
def client(request):
    test_client = APP.test_client()
    ctx = APP.app_context()
    ctx.push()
    yield test_client
    ctx.pop()

    def teardown():
        pass  # databases and resources have to be freed at the end. But so far we don't have anything

    request.addfinalizer(teardown)
    return test_client


def json_response(response):
    """Decode json from response"""
    return json.loads(response.data.decode('utf8'))


# PAGES TESTS

def test_route_page_welcome(client):
    """Test the client loads the homepage title  """
    response = client.get('/')
    assert response.status_code == 200
    assert b'Home | WikiDP' in response.data


def test_route_page_about(client):
    """Test the client loads the about title  """
    response = client.get('/about')
    assert response.status_code == 200
    assert b'About Wikidata For Digital Preservation | WikiDP' in response.data


def test_route_page_reports(client):
    """Test the client loads the reports title  """
    response = client.get('/reports')
    assert response.status_code == 200
    assert b'Reports | WikiDP' in response.data


def test_route_page_browse(client):
    """Test the client loads the browse title  """
    response = client.get('/browse')
    assert response.status_code == 200
    assert b'Browse Formats | WikiDP' in response.data


def test_route_page_unauthorized(client):
    """Test the client loads the 403 page  """
    response = client.get('/unauthorized', follow_redirects=True)
    assert response.status_code == 403
    assert b'You are not authorized to view this page' in response.data


def test_route_page_error(client):
    """Test the client loads the 500 page  """
    response = client.get('/error', follow_redirects=True)
    assert response.status_code == 500
    assert b'Internal Error' in response.data


def test_route_page_selected_item(client):
    """Test the client loads the preview of sample item  """
    response = client.get('/'+settings.SAMPLE_QID, follow_redirects=True)
    assert response.status_code == 200
    assert bytes(settings.SAMPLE_QID, encoding='utf-8') in response.data
    response = client.get('/'+settings.SAMPLE_QID_NOT_EXIST, follow_redirects=True)
    assert response.status_code == 404


def test_route_page_selected_item__lowercase(client):
    """Test the client loads the preview of sample item using lowercase id  """
    response = client.get('/'+settings.SAMPLE_QID.lower(), follow_redirects=True)
    assert response.status_code == 200
    assert bytes(settings.SAMPLE_QID, encoding='utf-8') in response.data
    response = client.get('/'+settings.SAMPLE_QID_NOT_EXIST.lower(), follow_redirects=True)
    assert response.status_code == 404


def test_route_item_preview(client):
    """Test the client loads the preview of sample item  """
    response = client.get('/'+settings.SAMPLE_QID+'/preview', follow_redirects=True)
    assert response.status_code == 200
    assert bytes(settings.SAMPLE_QID, encoding='utf-8') in response.data
    response = client.get('/'+settings.SAMPLE_QID_NOT_EXIST+'/preview', follow_redirects=True)
    assert response.status_code == 404


def test_route_item_contribute(client):
    """Test the client loads the contribute of sample item  """
    response = client.get('/'+settings.SAMPLE_QID+'/contribute', follow_redirects=True)
    assert response.status_code == 200
    assert bytes(settings.SAMPLE_QID, encoding='utf-8') in response.data
    response = client.get('/'+settings.SAMPLE_QID_NOT_EXIST+'/contribute', follow_redirects=True)
    assert response.status_code == 404

# TODO: Once a schema is added without a category add a test


def test_route_item_checklist_by_schema__with_category(client):
    response = client.get('/Q7715973/checklist/file_format/file_format_minimal.json')
    assert response.status_code == 200
    assert b'sidebar-property-li' in response.data


def test_route_item_checklist_by_schema__fake_schema(client):
    response = client.get('/Q7715973/checklist/fake_schema.json')
    assert response.status_code == 200
    assert b'no suggested properties in this schema' in response.data


# FORMS TEST
def test_route_form_preview_item(client):
    """Test the client loads the contribute of sample item  """
    response = client.post('/preview', follow_redirects=True,
                           data={'qid': 'Q7715973', 'optionList': '[["Q7715973", "TEST ELEMENT", "test description"]]'})
    assert response.status_code == 200
    assert b'Q7715973' in response.data
    assert b'TEST ELEMENT' in response.data
    assert b'test description' in response.data


def test_route_form_contribute_item(client):
    """Test the client loads the contribute of sample item  """
    response = client.post('/contribute', follow_redirects=True,
                           data={'qid': 'Q7715973', 'optionList': '[["Q7715973", "TEST ELEMENT", "test description"]]'})
    assert response.status_code == 200
    assert b'Q7715973' in response.data
    assert b'TEST ELEMENT' in response.data
    assert b'test description' in response.data


# SEARCH TESTS
def test_route_process_site_search__by_label(client):
    """Test the client loads the contribute of sample item  """
    response = client.post('/search', data={'userInput': 'debian'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Q7715973' in response.data


def test_route_process_site_search__by_puid(client):
    """Test the client loads the contribute of sample item  """
    response = client.post('/search', data={'userInput': 'fmt/354'}, follow_redirects=True)
    assert response.status_code == 200
    assert b'Q26543628' in response.data


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


def test_route_api_get_item(client):
    response = client.get('/api/Q7715973')
    assert response.status_code == 200
    assert json_response(response)['qid'] == 'Q7715973'


def test_route_api_get_property(client):
    response = client.get('/api/'+settings.SAMPLE_PID_STRING)
    assert response.status_code == 200
    assert json_response(response)['id']['value'] == settings.SAMPLE_PID_STRING
    assert 'propertyLabel' in json_response(response)


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

# TODO: MOCK Wikidata Requests/Responses
# def test_route_api_write_claims_to_item(client):
#     """
#     Currently Supporting:
#         1. WikibaseItem
#         2. String
#
#     TODO: Add all the data types
#     https://www.wikidata.org/wiki/Help:Data_type#List_of_data_types
#     """
#     claim_list = [ {
#             'pid': settings.SAMPLE_PID_WIKIBASEITEM__TEST,
#             'value': settings.SAMPLE_QID__TEST,
#             'type': 'WikibaseItem'
#         },
#             {
#             'pid': settings.SAMPLE_PID_STRING__TEST,
#             'value': 'Test String',
#             'type': 'String'
#         }
#         ]
#     response = client.post('/api/'+settings.SAMPLE_QID__TEST+'/claims/write',
#                             data=json.dumps(claim_list),
#                             content_type='application/json',
#                             follow_redirects=True)
#     res = json_response(response)
#     assert response.status_code == 200
#     assert res['status'] == 'success'
#     assert len(res['successful_claims']) == len(claim_list)
#     assert len(res['failure_claims']) == 0
#
# def test_route_api_write_claims_to_item__errors(client):
#     """
#     Claim List Errors:
#         1. Item Value with Non-existent item
#         2. Item Value passed with random string
#
#     """
#     claim_list = [ {
#             'pid': settings.SAMPLE_PID_WIKIBASEITEM__TEST,
#             'value': settings.SAMPLE_QID_NOT_EXIST__TEST,
#             'type': 'WikibaseItem'
#         },
#             {
#             'pid': settings.SAMPLE_PID_WIKIBASEITEM__TEST,
#             'value': 'Test String',
#             'type': 'WikibaseItem'
#         }
#         ]
#     response = client.post('/api/'+settings.SAMPLE_QID__TEST+'/claims/write',
#                             data=json.dumps(claim_list),
#                             content_type='application/json',
#                             follow_redirects=True)
#     res = json_response(response)
#     assert response.status_code == 200
#     assert res['status'] == 'success'
#     assert len(res['failure_claims']) == len(claim_list)
#     assert len(res['successful_claims']) == 0
