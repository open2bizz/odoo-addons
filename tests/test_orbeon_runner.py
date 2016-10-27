# -*- encoding: utf-8 -*-
##############################################################################
#
#    open2bizz
#    Copyright (C) 2016 open2bizz (open2bizz.nl).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo.tests.common import TransactionCase

from test_orbeon_common import TestOrbeonCommon, TODO

from lxml import etree, objectify

import logging

_logger = logging.getLogger(__name__)

class TestOrbeonRunner(TestOrbeonCommon):
    """Tests for Orbeon Runner Forms"""

    @TODO
    def test_write_invalidate_change_builder_id(self):
        """Test updating the builder_id is not allowed"""
    
    def test_orbeon_search_read_new_notstored_by_orbeon_persistence(self):
        """Test reading a new runner form, where xml (field) is empty - isn't stored yet (by
        Orbeon persistence).  It should contain the xml value from the
        <form>node in it's linked orbeon_builder.xml (field)
        """
        domain = [('id', '=', self.runner_form_a_v1_new.id)]
        rec = self.runner_model.orbeon_search_read_data(domain, ['xml'])

        self.assertXmlEquivalentOutputs(rec['xml'], self.xmlFromFile('test_orbeon4.10_runner_form_a_v1_new.xml'))

    def test_orbeon_search_read_stored_by_orbeon_persistence_simple(self):
        """Test reading a simple runner form, stored by the Orbeon persistence - with xml
        (field) value.  It should contain it's own stored XML value.
        """
        runner_1_domain = [('id', '=', self.runner_form_a_v1.id)]
        runner_1_rec = self.runner_model.orbeon_search_read_data(runner_1_domain, ['xml'])
        self.assertXmlEquivalentOutputs(runner_1_rec['xml'], self.xmlFromFile('test_orbeon4.10_runner_form_a_v1.xml'))

        runner_2_domain = [('id', '=', self.runner_form_a_v2.id)]
        runner_2_rec = self.runner_model.orbeon_search_read_data(runner_2_domain, ['xml'])
        self.assertXmlEquivalentOutputs(runner_2_rec['xml'], self.xmlFromFile('test_orbeon4.10_runner_form_a_v2.xml'))

    @TODO
    def test_orbeon_search_read_stored_by_orbeon_persistence_with_ERP_fieds(self):
        """Test reading a runner form with ERP-fields, stored by the Orbeon
        persistence - with xml (field) value.  It should contain it's own
        stored XML value with ERP-field values from the
        model-object-fields.
        """

    @TODO
    def test_orbeon_search_read_should_merge(self):
        """Test orbeon_search_read, where Runner field `is_merged` is False and
        there's a new builder current-version. So in this case it should
        trigger a merge.
        """

    @TODO
    def test_orbeon_search_read_should_not_merge_is_merged(self):
        """Test orbeon_search_read, where Runner field `is_merged` is True and
        there's no newer builder current-version. So in this case it should
        not trigger a merge.
        """

    @TODO
    def test_orbeon_search_read_should_not_merge_current_builder_remains_same(self):
        """Test orbeon_search_read, where Runner field `is_merged` is False and
        there's no newer builder current-version. So in this case it should
        not trigger a merge.
        """

    @TODO
    def test_merge_basic_only_orbeon_fieldcontrols(self):
        """Test merge basic XML-form with only Orbeon fieldcontrols. This tests the base
        merge merge API/functions.
        """

        return

        xml = self.runner_form_a_v1.merge_xml_current_builder()
        root = self.assertXmlDocument(xml)

        # Original data not
        self.assertXpathsOnlyOne(root, ['//input-control-1'])
        self.assertXpathValues(root, '//input-control-1/text()', ('antwoord 1'))

        # New controls
        self.assertXpathsOnlyOne(root, ['//input-control-2', '//data-control-1'])
        

    @TODO
    def test_merge_nocopy_NC_field(self):
        """Test merge but ignore/skip nocopy (NC.) field"""
        
        return

        nocopy_field = "NC.input-control-3"

        xml = self.runner_form_a_v2_nocopy.merge_xml_current_builder()
        root = self.assertXmlDocument(xml)

        # Original data not
        self.assertXpathsOnlyOne(root, ['//input-control-1'])
        self.assertXpathValues(root, '//input-control-1/text()', ('antwoord 1'))

        # New controls
        self.assertXpathsOnlyOne(root, ['//input-control-2', '//data-control-1'])
        
        msg = ("Field %s shouldn't be copied, but it was!" % nocopy_field)
