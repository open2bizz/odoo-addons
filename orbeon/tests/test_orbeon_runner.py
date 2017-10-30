# -*- coding: utf-8 -*-
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

from odoo.exceptions import ValidationError

from test_orbeon_common import TestOrbeonCommon
from utils import TODO
from ..services import runner_xml_parser

from orbeon_xml_api.runner import Runner as RunnerAPI
from lxml import etree

import logging

_logger = logging.getLogger(__name__)


class TestOrbeonRunner(TestOrbeonCommon):
    """Tests for Orbeon Runner Forms"""

    def test_write_invalidate_change_builder_id(self):
        """Test changing the builder_id is not allowed"""
        with self.assertRaisesRegexp(ValidationError, 'Changing the builder is not allowed.'):
            self.runner_form_a_v1.sudo().write(
                {
                    'builder_id': self.builder_form_a_v2_current,
                }
            )

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

        """
        runner_form_a_v1
        """
        domain = [('id', '=', self.runner_form_a_v1.id)]
        runner = self.runner_model.orbeon_search_read_data(domain, ['xml'])

        self.assertXmlEquivalentOutputs(runner['xml'], self.xmlFromFile('test_orbeon4.10_runner_form_a_v1.xml'))

        root = self.assertXmlDocument(runner['xml'])
        self.assertXpathValues(root, '//input-control-1/text()', ['text 1'])

        root_with_changes = etree.fromstring(runner['xml'])
        root_with_changes.xpath('//input-control-1')[0].text = 'this is text 1'
        xml_with_changes = etree.tostring(root_with_changes)

        # Save directly (bypass Orbeon)
        self.runner_form_a_v1.sudo().write({
            'xml': xml_with_changes
        })

        runner_with_changes = self.runner_model.orbeon_search_read_data(domain, ['xml'])

        root = self.assertXmlDocument(runner_with_changes['xml'])
        self.assertXpathValues(root, '//input-control-1/text()', ['this is text 1'])

        """
        runner_form_a_v2
        """
        domain = [('id', '=', self.runner_form_a_v2.id)]
        runner = self.runner_model.orbeon_search_read_data(domain, ['xml'])

        self.assertXmlEquivalentOutputs(runner['xml'], self.xmlFromFile('test_orbeon4.10_runner_form_a_v2.xml'))

        root = self.assertXmlDocument(runner['xml'])
        self.assertXpathValues(root, '//input-control-1/text()', ['text 1'])
        self.assertXpathValues(root, '//input-control-2/text()', ['text 2'])
        self.assertXpathValues(root, '//date-control-1/text()', ['2016-05-11'])

        root_with_changes = etree.fromstring(runner['xml'])
        root_with_changes.xpath('//input-control-1')[0].text = 'this is text 1'
        root_with_changes.xpath('//input-control-2')[0].text = 'this is text 2'
        root_with_changes.xpath('//date-control-1')[0].text = '2017-01-10'
        xml_with_changes = etree.tostring(root_with_changes)

        # Save directly (bypass Orbeon)
        self.runner_form_a_v2.sudo().write({
            'xml': xml_with_changes
        })

        runner_with_changes = self.runner_model.orbeon_search_read_data(domain, ['xml'])

        root = self.assertXmlDocument(runner_with_changes['xml'])
        self.assertXpathValues(root, '//input-control-1/text()', ['this is text 1'])
        self.assertXpathValues(root, '//input-control-2/text()', ['this is text 2'])
        self.assertXpathValues(root, '//date-control-1/text()', ['2017-01-10'])

    def test_orbeon_search_read_with_ERP_fieds(self):
        """Test reading a runner form with ERP-fields (model-object-fields)."""

        domain = [('id', '=', self.runner_form_c_erp_fields_v1.id)]
        rec = self.runner_model.orbeon_search_read_data(domain, ['xml'])
        root = self.assertXmlDocument(rec['xml'])

        self.assertXpathsOnlyOne(root, ['//ERP.name'])
        self.assertXpathValues(root, '//ERP.name/text()', [('Administrator')])

        self.assertXpathsOnlyOne(root, ['//ERP.login'])
        self.assertXpathValues(root, './/ERP.login/text()', [('admin')])

        self.assertXpathsOnlyOne(root, ['//ERP.company_id.name'])
        self.assertXpathValues(root, './/ERP.company_id.name/text()', [('YourCompany')])

        self.assertXpathsOnlyOne(root, ['//ERP.company_id.currency_id.name'])
        self.assertXpathValues(root, './/ERP.company_id.currency_id.name/text()', [('EUR')])

    def test_orbeon_search_read_with_ERP_fieds_changed_ERP_object(self):
        """Test reading a runner form with ERP-fields on changed ERP model-object."""

        domain = [('id', '=', self.runner_form_c_erp_fields_v1.id)]

        # Update some fields in ERP-object
        self.user_1.sudo().write({
            'name': 'Dummy',
            'login': 'dummy_login'
        })

        rec = self.runner_model.orbeon_search_read_data(domain, ['xml'])
        root = self.assertXmlDocument(rec['xml'])

        self.assertXpathsOnlyOne(root, ['//ERP.name'])
        self.assertXpathValues(root, '//ERP.name/text()', [('Dummy')])

        self.assertXpathsOnlyOne(root, ['//ERP.login'])
        self.assertXpathValues(root, './/ERP.login/text()', [('dummy_login')])

    def test_orbeon_search_read_with_unknown_ERP_fieds(self):
        """Test reading a runner form with unknown ERP-fields (model-object)."""

        domain = [('id', '=', self.runner_form_c_erp_fields_v1.id)]
        rec = self.runner_model.orbeon_search_read_data(domain, ['xml'])
        root = self.assertXmlDocument(rec['xml'])

        unknown_erp_field = runner_xml_parser.xml_parser_erp_fields.UNKNOWN_ERP_FIELD

        self.assertXpathsOnlyOne(root, ['//ERP.unknown_field'])
        self.assertXpathValues(root, './/ERP.unknown_field/text()', [(unknown_erp_field)])

        self.assertXpathsOnlyOne(root, ['//ERP.unknown_field_id.name'])
        self.assertXpathValues(root, './/ERP.unknown_field_id.name/text()', [(unknown_erp_field)])

        self.assertXpathsOnlyOne(root, ['//ERP.company_id.unknown_field'])
        self.assertXpathValues(root, './/ERP.company_id.unknown_field/text()', [(unknown_erp_field)])

        self.assertXpathsOnlyOne(root, ['//ERP.company_id.unknown_field_id.name'])
        self.assertXpathValues(root, './/ERP.company_id.unknown_field_id.name/text()', [(unknown_erp_field)])

    def test_orbeon_search_read_stored_by_orbeon_persistence_with_ERP_fieds(self):
        """Test reading a runner form with ERP-fields, stored by the Orbeon
        persistence - with xml (field) value.  It should contain it's own
        stored XML value with ERP-field values from the
        model-object-fields.
        """

        domain = [('id', '=', self.runner_form_c_erp_fields_v1.id)]
        rec = self.runner_model.orbeon_search_read_data(domain, ['xml'])

        # Check initial, if empty
        root_initial = self.assertXmlDocument(rec['xml'])

        self.assertXpathValues(root_initial, '//nickname/text()', [])
        self.assertXpathValues(root_initial, '//notes/text()', [])

        # Change
        root_with_changes = etree.fromstring(rec['xml'])
        root_with_changes.xpath('//nickname')[0].text = 'Batman'
        root_with_changes.xpath('//notes')[0].text = 'Batman has Orbeon superpowers'

        xml_with_changes = etree.tostring(root_with_changes)

        self.runner_form_c_erp_fields_v1.sudo().write({
            'xml': xml_with_changes
        })

        # Test change and whether rest of XML-doc stayed the same
        self.runner_form_c_erp_fields_v1.refresh()

        root = self.assertXmlDocument(self.runner_form_c_erp_fields_v1.xml)

        self.assertXpathValues(root, '//nickname/text()', ['Batman'])
        self.assertXpathValues(root, '//notes/text()', ['Batman has Orbeon superpowers'])

        self.assertXpathsOnlyOne(root, ['//ERP.name'])
        self.assertXpathValues(root, '//ERP.name/text()', [('Administrator')])

        self.assertXpathsOnlyOne(root, ['//ERP.login'])
        self.assertXpathValues(root, './/ERP.login/text()', [('admin')])

        self.assertXpathsOnlyOne(root, ['//ERP.company_id.name'])
        self.assertXpathValues(root, './/ERP.company_id.name/text()', [('YourCompany')])

        self.assertXpathsOnlyOne(root, ['//ERP.company_id.currency_id.name'])
        self.assertXpathValues(root, './/ERP.company_id.currency_id.name/text()', [('EUR')])

    def test_can_not_merge(self):
        """Test should NOT merge, where Runner field `is_merged` is False and
        there's a new builder current-version. So in this case it should
        trigger a merge.
        """
        # First version and default (also empty XML) don't merge
        self.assertFalse(self.runner_form_a_v1_new.can_merge())

        # Second version (empty XML)
        self.assertFalse(self.runner_form_a_v1_new.can_merge())

        # Runner (Form) version 2, already merged.
        self.runner_form_a_v2_new.is_merged = True
        self.assertFalse(self.runner_form_a_v2_new.can_merge())

    def test_can_merge(self):
        """Test should NOT merge, where Runner field `is_merged` is False and
        there's a new builder current-version. So in this case it should
        trigger a merge.
        """
        # Runner version 1, can be merged.
        self.assertTrue(self.runner_form_a_v1.can_merge())

        # Runner version 2, already the last current one (can't merge)
        self.assertFalse(self.runner_form_a_v2.can_merge())

        # Merge Runner version 1. Afterwards can't merge
        self.runner_form_a_v1.merge_current_builder()
        self.assertFalse(self.runner_form_a_v1.can_merge())

    def test_merge_current_builder_basic(self):
        """Test merge basic XML-form with only Orbeon fieldcontrols. This tests the base
        merge merge API/functions.
        """
        current_builder = self.runner_form_a_v1.builder_id.current_builder_id
        before_merge_runner_api = RunnerAPI(self.runner_form_a_v1.xml, None, self.runner_form_a_v1.builder_id.xml)

        self.assertEqual(before_merge_runner_api.form.inputcontrol1.label, 'Input 1')
        self.assertEqual(before_merge_runner_api.form.inputcontrol1.value, 'text 1')
        self.assertEqual(before_merge_runner_api.form.inputcontrol1._parent._bind.name, 'section-1')

        merged_runner = self.runner_form_a_v1.sudo().merge_current_builder()
        self.runner_form_a_v1.refresh()

        # Check orbeon.runner info
        self.assertTrue(merged_runner.is_merged)
        self.assertEqual(merged_runner.builder_id.id, current_builder.id)

        # Old form/data still there (not harmed by the merge)
        merged_runner_api = RunnerAPI(self.runner_form_a_v1.xml, None, current_builder.xml)

        self.assertEqual(merged_runner_api.form.inputcontrol1.label, 'Input 1')
        self.assertEqual(merged_runner_api.form.inputcontrol1.value, 'text 1')
        self.assertEqual(merged_runner_api.form.inputcontrol1._parent._bind.name, 'section-1')

        # Some new freshly merged controls (from builder)
        self.assertEqual(merged_runner_api.form.inputcontrol2.label, 'Input 2')
        self.assertEqual(merged_runner_api.form.inputcontrol2.value, None)
        self.assertEqual(merged_runner_api.form.inputcontrol2._parent._bind.name, 'section-1')

        self.assertEqual(merged_runner_api.form.datecontrol1.label, 'Date 1')
        self.assertEqual(merged_runner_api.form.datecontrol1.value, None)
        self.assertEqual(merged_runner_api.form.datecontrol1._parent._bind.name, 'section-1')

    def test_copy_and_merge_current_builder(self):
        before_runner = self.runner_form_a_v1
        before_root = self.assertXmlDocument(before_runner.xml)

        # First check to be merged controls aren't present yet
        self.assertXpathsOnlyOne(before_root, ['//input-control-1'])
        self.assertXpathValues(before_root, './/input-control-1/text()', [('text 1')])

        self.assertEqual(len(before_root.xpath('//input-control-2')), 0)
        self.assertEqual(len(before_root.xpath('//date-control-1')), 0)

        # Copy (and merge)
        after_runner = before_runner.sudo().copy()
        after_root = self.assertXmlDocument(after_runner.xml)

        self.assertFalse(after_runner.can_merge())

        self.assertXpathsOnlyOne(after_root, ['//input-control-1'])
        self.assertXpathValues(after_root, './/input-control-1/text()', [('text 1')])

        self.assertXpathsOnlyOne(after_root, ['//input-control-2'])
        # Assert text is empty
        self.assertXpathValues(after_root, './/input-control-2/text()', [])

        self.assertXpathsOnlyOne(after_root, ['//date-control-1'])
        # Assert text is empty
        self.assertXpathValues(after_root, './/date-control-1/text()', [])

    @TODO
    def test_merge_nocopy_NC_field(self):
        """Test merge but ignore/skip nocopy (NC.) field"""

        return

        # nocopy_field = "NC.input-control-3"

        xml = self.runner_form_a_v2_nocopy.merge_xml_current_builder()
        root = self.assertXmlDocument(xml)

        # Original data not
        self.assertXpathsOnlyOne(root, ['//input-control-1'])
        self.assertXpathValues(root, '//input-control-1/text()', ('text 1'))

        # New controls
        self.assertXpathsOnlyOne(root, ['//input-control-2', '//data-control-1'])

        # msg = ("Field %s shouldn't be copied, but it was!" % nocopy_field)
