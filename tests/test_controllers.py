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
"""Unit tests for WikiDP Controllers."""
from unittest import TestCase

from tests import settings
from wikidp.controllers import pages as pages_controller


class ControllerTests(TestCase):
    # Pages Controllers
    def test_controller_pages_get_checklist_context__no_schema(self):
        output = pages_controller.get_property_checklist_from_schema(settings.SAMPLE_QID)
        self.assertEqual(output, [])
