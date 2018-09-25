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
from odoo.tests.common import TransactionCase
from odoo.exceptions import UserError, ValidationError

from test_orbeon_common import TestOrbeonCommon
from utils import TODO

from ..models import orbeon_builder
from ..models import orbeon_runner

from psycopg2 import IntegrityError
from lxml import etree

import logging

_logger = logging.getLogger(__name__)

class TestOrbeonBuilder(TestOrbeonCommon):
    """Tests for Orbeon Builder Forms"""

    def test_create_successful(self):
        """Test create several successful"""

        default_form_name = 'test-builder-1'
        default_form_title = 'Test Builder 1'
        
        form_name = 'test_create_successful'
        form_title = 'Test Create Successful'
        
        # create 1
        try:
            record = self.builder_model.sudo().create(
                {
                    'name': form_name,
                    'title': form_title,
                    'version_comment': 'version 1',
                    'server_id': self.server_1.id,
                    'builder_template_id': self.builder_template_form_1.id
                    # 'state': 'new' # which is the default
                    # 'version': 1 # which is the default
                }
            )
        except Exception as e:
            self.fail(e)

        xml = etree.fromstring(record.xml)

        xml_xh_title = xml.xpath('//xh:title', namespaces={'xh': "http://www.w3.org/1999/xhtml"})[0]
        self.assertEquals(xml_xh_title.text, form_title)

        xml_form_name = xml.xpath('//form-name')[0]
        self.assertEquals(xml_form_name.text, form_name)

        xml_title = xml.xpath('//title')[0]
        self.assertEquals(xml_title.text, form_title)

        xml_xh_title.text = default_form_title
        xml_form_name.text = default_form_name
        xml_title.text = default_form_title

        self.assertXmlEquivalentOutputs(etree.tostring(xml), self.builder_template_form_1.xml)

        # create 2
        try:
            record = self.builder_model.sudo().create(
                {
                    'name': form_name,
                    'title': form_title,
                    'version_comment': 'version 1',
                    'server_id': self.server_1.id,
                    'state': orbeon_builder.STATE_NEW,
                    'version': 2,
                    'builder_template_id': self.builder_template_form_1.id
                }
            )
        except Exception as e:
            self.fail(e)

        xml = etree.fromstring(record.xml)

        xml_xh_title = xml.xpath('//xh:title', namespaces={'xh': "http://www.w3.org/1999/xhtml"})[0]
        self.assertEquals(xml_xh_title.text, form_title)

        xml_form_name = xml.xpath('//form-name')[0]
        self.assertEquals(xml_form_name.text, form_name)

        xml_title = xml.xpath('//title')[0]
        self.assertEquals(xml_title.text, form_title)

        xml_xh_title.text = default_form_title
        xml_form_name.text = default_form_name
        xml_title.text = default_form_title

        self.assertXmlEquivalentOutputs(etree.tostring(xml), self.builder_template_form_1.xml)

        # create 3
        try:
            record = self.builder_model.sudo().create(
                {
                    'name': form_name,
                    'title': form_title,
                    'version_comment': 'version 1',
                    'server_id': self.server_1.id,
                    'builder_template_id': self.builder_template_form_1.id,
                    'state': orbeon_builder.STATE_CURRENT,
                    'version': 3,
                }
            )
        except Exception as e:
            self.fail(e)

        xml = etree.fromstring(record.xml)

        xml_xh_title = xml.xpath('//xh:title', namespaces={'xh': "http://www.w3.org/1999/xhtml"})[0]
        self.assertEquals(xml_xh_title.text, form_title)

        xml_form_name = xml.xpath('//form-name')[0]
        self.assertEquals(xml_form_name.text, form_name)

        xml_title = xml.xpath('//title')[0]
        self.assertEquals(xml_title.text, form_title)

        xml_xh_title.text = default_form_title
        xml_form_name.text = default_form_name
        xml_title.text = default_form_title

        self.assertXmlEquivalentOutputs(etree.tostring(xml), self.builder_template_form_1.xml)

    def test_write_successful(self):
        """Test write several successful"""

        # write: version_comment
        try:
            self.builder_form_a_v1.sudo().write(
                {
                    'version_comment': 'test version builder 1'
                }
            )
        except Exception as e:
            self.fail(e)

        # write: xml
        try:
            self.builder_form_a_v1.sudo().write(
                {
                    'xml': '<?xml version="1.0"?><odoo></odoo>'
                }
            )
        except Exception as e:
            self.fail(e)

        xml_v2 = self.xmlFromFile('test_orbeon4.10_builder_form_a_v2.xml')
        
        self.builder_form_a_v1.sudo().write(
            {
                'xml': xml_v2
            }
        )

        self.builder_form_a_v1.refresh()
        self.assertXmlEquivalentOutputs(self.builder_form_a_v1.xml, xml_v2)
        
        # write: state
        try:
            self.builder_form_a_v2_current.sudo().write(
                {
                    'state': orbeon_builder.STATE_NEW,
                }
            )
            
            self.builder_form_a_v1.sudo().write(
                {
                    'state': orbeon_builder.STATE_CURRENT,
                }
            )
        except Exception as e:
            self.fail(e)

    def test_create_with_builder_template_xml_from_server(self):
        """Test create with Builder Template XML"""

        record = self.builder_model.sudo().create(
            {
                'name': 'test-builder-1',
                'title': 'Test Builder 1',
                'version_comment': 'version 1',
                'server_id': self.server_1.id,
                'builder_template_id': self.builder_template_form_1.id
            }
        )

        self.assertXmlEquivalentOutputs(record.xml, self.builder_template_form_1.xml)

    def test_create_name_required(self):
        """Test create with a missing, but required, name"""
        with self.assertRaisesRegexp(IntegrityError, 'column "name" violates not-null'):
            self.builder_model.sudo().create(
                {
                    'version_comment': 'version 1',
                    'server_id': self.server_1.id,
                    'builder_template_id': self.builder_template_form_1.id
                }
            )

    def test_write_name_required(self):
        """Test write with a missing, but required, name"""
        with self.assertRaisesRegexp(IntegrityError, 'column "name" violates not-null'):
            self.builder_form_a_v1.sudo().write(
                {
                    'name': None,
                    'version_comment': 'cleared name',
                }
            )

    def test_create_invalid_name(self):
        """Test create with name containing illegal chararacters"""

        invalid_names = [
            'test form',
            'Test Form',
            '/testform',
            'test/form',
            'test/form/',
            '?testform',
            'test?form',
            'testform?',
            ':testform',
            'test:form',
            'testform:',
            '/test?form/bla#',
            'test-1#form',
        ]

        for name in invalid_names:
            with self.assertRaisesRegexp(ValidationError, 'Name is invalid. Use ASCII letters, digits, "-" or "_"'):
                self.builder_model.sudo().create(
                    {
                        'name': name,
                        'version_comment': 'version 1',
                        'server_id': self.server_1.id,
                        'builder_template_id': self.builder_template_form_1.id
                    }
                )

    def test_write_invalid_name(self):
        """Test write with name containing illegal chararacters"""

        invalid_names = [
            'test form',
            'Test Form',
            '/testform',
            'test/form',
            'test/form/',
            '?testform',
            'test?form',
            'testform?',
            ':testform',
            'test:form',
            'testform:',
            '/test?form/bla#',
            'test-1#form',
        ]

        for name in invalid_names:
            with self.assertRaisesRegexp(ValidationError, 'Name is invalid. Use ASCII letters, digits, "-" or "_"'):
                self.builder_form_a_v1.sudo().write(
                    {
                        'name': name,
                        'version_comment': 'version 1',
                        'server_id': self.server_1.id
                    }
                )

    def test_create_title_notrequired(self):
        """Test create with a missing, but not-required, title"""

        try:
            record = self.builder_model.sudo().create(
                {
                    'name': 'test_create_title_notrequired',
                    'version_comment': 'some version',
                    'server_id': self.server_1.id,
                    'builder_template_id': self.builder_template_form_1.id
                }
            )
        except Exception as e:
            self.fail(e)
            
    def test_write_title_notrequired(self):
        """Test write with a missing, but not required, title"""

        try:
            record = self.builder_form_a_v1.sudo().write(
                {
                    'title': False,
                }
            )
        except Exception as e:
            self.fail(e)

    def test_create_version_comment_required(self):
        """Test create with a missing, but required, version_comment"""
        with self.assertRaisesRegexp(IntegrityError, 'column "version_comment" violates not-null'):
            self.builder_model.sudo().create(
                {
                    'name': 'test_create_version_comment_required',
                    'server_id': self.server_1.id,
                    'builder_template_id': self.builder_template_form_1.id
                }
            )

    def test_write_version_comment_required(self):
        """Test write with a missing, but required, version_comment"""
        with self.assertRaisesRegexp(IntegrityError, 'column "version_comment" violates not-null'):
            self.builder_form_a_v1.sudo().write(
                {
                    'name': 'test_write_version_comment_required',
                    'server_id': self.server_1.id,
                    'version_comment': None,
                }
            )

    def test_version_is_readonly(self):
        """Test version field is readonly"""
        field = self.builder_model._fields['version']
        self.assertTrue(field.readonly)

    @TODO
    def test_create_version_increment_in_sequence(self):
        """Test create version increments by 1 (in sequence)"""

    @TODO
    def test_write_version_increment_in_sequence(self):
        """Test create version increments by 1 (in sequence)"""
        
    @TODO
    def test_crreate_version_increment_in_sequence(self):
        """Test create version increments by 1 (in sequence)"""

    @TODO
    def test_write_version_increment_in_sequence(self):
        """Test create version increments by 1 (in sequence)"""
    
    def test_create_constraint_version_unique_by_name(self):
        """Test create with unique version by name"""

        # check version 1 exists
        domain_filter = [('name', '=', self.builder_form_a_v1.name), ('version', '=', 1)]
        builder_version_1 = self.builder_model.search(domain_filter)
        self.assertEquals(builder_version_1.version, 1)

        with self.assertRaisesRegexp(ValidationError, 'already has a record with version'):
            self.builder_model.sudo().create(
                {
                    'name': self.builder_form_a_v1.name,
                    'version_comment': 'version 1',
                    'server_id': self.server_1.id,
                    'builder_template_id': self.builder_template_form_1.id,
                    'version': 1,
                }
            )

    def test_write_constraint_version_unique_by_name(self):
        """Test write with unique version by name"""

        # check version 1 exists
        domain_filter = [('name', '=', self.builder_form_a_v1.name), ('version', '=', 1)]
        builder_version_1 = self.builder_model.search(domain_filter)
        self.assertEquals(builder_version_1.version, 1)

        # duplicate and update version to 1
        self.builder_form_a_v1.new_version_builder_form()
        domain_filter = [('name', '=', self.builder_form_a_v1.name), ('version', '=', 2)]
        builder_version_2 = self.builder_model.search(domain_filter)

        with self.assertRaisesRegexp(ValidationError, 'already has a record with version'):
            builder_version_2.write(
                {
                    'version': 1
                }
            )

    def test_create_constraint_state_current_unique_by_name(self):
        """Test create with unique "current" state by name"""
        
        # check a current exists
        domain_filter = [('name', '=', self.builder_form_a_v2_current.name), ('state', '=', orbeon_builder.STATE_CURRENT)]
        builder_current = self.builder_model.search(domain_filter)
        self.assertEquals(builder_current.state, orbeon_builder.STATE_CURRENT)

        with self.assertRaisesRegexp(ValidationError, "already has a record with status 'current'"):
            self.builder_model.sudo().create(
                {
                    'name': builder_current.name,
                    'version_comment': 'version foobar',
                    'server_id': self.server_1.id,
                    'builder_template_id': self.builder_template_form_1.id,
                    'version': builder_current.version + 1,
                    'state': orbeon_builder.STATE_CURRENT,
                }
            )

    def test_write_constraint_state_current_unique_by_name(self):
        """Test write with unique "current" state by name"""

                # check a current exists
        domain_filter = [('name', '=', self.builder_form_a_v2_current.name), ('state', '=', orbeon_builder.STATE_CURRENT)]
        builder_current = self.builder_model.search(domain_filter)
        self.assertEquals(builder_current.state, orbeon_builder.STATE_CURRENT)

        # duplicate and update version to 1
        self.builder_form_a_v2_current.new_version_builder_form()
        domain_filter = [('name', '=', self.builder_form_a_v2_current.name), ('version', '=', self.builder_form_a_v2_current.version + 1)]
        builder_current_duplicated = self.builder_model.search(domain_filter)

        with self.assertRaisesRegexp(ValidationError, "already has a record with status 'current'"):
            builder_current_duplicated.write(
                {
                    'state': orbeon_builder.STATE_CURRENT
                }
            )

    def test_create_allow_new_version_by_unique_name_and_version(self):
        """Test create allow duplicate builder names with unique version, where state IS NOT current"""

        # Create a 3rd version of OrbeonBuilder form with name: form_a
        try:
            record = self.builder_model.sudo().create(
                {
                    'name': self.builder_form_a_v2_current.name,
                    'title': self.builder_form_a_v2_current.title,
                    'version_comment': 'test_create_allow_new_version_by_unique_name_and_version',
                    'server_id': self.server_1.id,
                    'builder_template_id': self.builder_template_form_1.id,
                    'version': 3
                }
            )
        except Exception as e:
            self.fail(e)

    def test_write_allow_new_version_by_unique_name_and_version(self):
        """Test write allow new_version builder names with unique version, where state IS NOT current"""

        # First create a unique 1st version of a OrbeonBuilder form
        # Then update the name (and version = 3), to name of an existing OrbeonBuilder form: form_a
        try:
            record = self.builder_model.sudo().create(
                {
                    'name': 'test_write_allow_new_version_by_unique_name_and_version',
                    'title': self.builder_form_a_v2_current.title,
                    'version_comment': 'test_write_allow_new_version_by_unique_name_and_version',
                    'server_id': self.server_1.id,
                    'builder_template_id': self.builder_template_form_1.id
                }
            )

            record.write({'name': self.builder_form_a_v1.name, 'version': 3})
        except Exception as e:
            self.fail(e)

    def test_create_server_id_required(self):
        """Test create with a missing, but required, server_id"""
        with self.assertRaisesRegexp(IntegrityError, 'column "server_id" violates not-null'):
            self.builder_model.sudo().create(
                {
                    'name': 'test_create_server_id_required',
                    'version_comment': 'version 1',
                    'builder_template_id': self.builder_template_form_1.id
                }
            )

    def test_write_server_id_required(self):
        """Test write with a missing, but required, server_id"""
        with self.assertRaisesRegexp(IntegrityError, 'column "server_id" violates not-null'):
            self.builder_form_a_v1.sudo().write(
                {
                    'name': 'test_write_server_id_required',
                    'version_comment': 'version 1',
                    'xml': '<?xml version="1.0"?><odoo></odoo>',
                    'server_id': None,
                }
            )

    @TODO
    def test_create_server_id_unknown(self):
        """Test create with an unknown (non-existing record) server"""

    @TODO
    def test_write_server_id_unknown(self):
        """Test write with an unknown (non-existing record) server"""

    @TODO
    def test_validate_create_xml_provided_both_template_and_xml(self):
        """Test create with both provided 'Orbeon Builder Template' and XML"""
        # Function validate_create_xml() in orbeon.builder

    @TODO
    def test_validate_create_xml_missing_both_template_and_xml(self):
        """Test create with missing 'Orbeon Builder Template' and XML"""
        # Function validate_create_xml() in orbeon.builder

    @TODO
    def test_unlink_builder_template_dont_cascade_unlink(self):
        """Test unlink the builder_template(_id) and the builder shouldn't be unlinked"""

    def test_write_xml_successful(self):
        """Test write XML successful"""

        try:
            self.builder_form_a_v1.sudo().write(
                {
                    'xml': '<?xml version="1.0"?><odoo></odoo>'
                }
            )
        except Exception as e:
            self.fail(e)

        with self.assertRaises(AssertionError):
            self.assertXmlEquivalentOutputs(self.builder_form_a_v1.xml, self.builder_form_a_v1.builder_template_id.xml)

    def test_delete_contains_runner_forms(self):
        """Test delete with references to orbeon.runner(forms)"""

        with self.assertRaises(IntegrityError):
            self.builder_form_a_v1.sudo().unlink()

    def test_delete_contains_no_runner_forms(self):
        """Test delete with NO references to orbeon.runner(forms)"""

        try:
            self.builder_form_b_no_runner_forms.unlink()
        except Exception as e:
            self.fail(e)        

    def test_orbeon_search_read_new_notstored_by_orbeon_persistence(self):
        """Test reading a new Builder form, where xml (field) is empty - isn't stored yet (by
        Orbeon persistence).  It should contain the xml value from the
        <form>node in it's linked builder_template_id.xml (field)
        """
        domain = [('id', '=', self.builder_form_a_v1.id)]
        rec = self.builder_model.orbeon_search_read_data(domain, ['xml', 'name', 'title'])

        xml_model = self.builder_form_a_v1.builder_template_id.xml
        root_xml_model = etree.fromstring(xml_model)
        root_xml_model.xpath('//form-name')[0].text = rec['name']
        root_xml_model.xpath('//xh:title', namespaces={'xh': "http://www.w3.org/1999/xhtml"})[0].text = rec['title']
        root_xml_model.xpath('//title')[0].text = rec['title']

        self.assertXmlEquivalentOutputs(rec['xml'], etree.tostring(root_xml_model))

        xml_file = self.xmlFromFile('test_orbeon4.10_builder_default.xml')
        root_xml_file = etree.fromstring(xml_file)
        root_xml_file.xpath('//form-name')[0].text = rec['name']        
        root_xml_file.xpath('//xh:title', namespaces={'xh': "http://www.w3.org/1999/xhtml"})[0].text = rec['title']
        root_xml_file.xpath('//title')[0].text = rec['title']

        self.assertXmlEquivalentOutputs(rec['xml'], etree.tostring(root_xml_file))

    def test_orbeon_search_read_stored_by_orbeon_persistence_simple(self):
        """Test reading a simple Builder form, stored by the Orbeon persistence - with xml
        (field) value.  It should contain it's own stored XML value.
        """
        domain = [('id', '=', self.builder_form_a_v2_current.id)]
        rec = self.builder_model.orbeon_search_read_data(domain, ['xml'])
        
        self.assertXmlEquivalentOutputs(rec['xml'], self.xmlFromFile('test_orbeon4.10_builder_form_a_v2.xml'))

    def test_new_version_builder_form(self):
        """Test make new_version (copy) of builder form"""
        name_filter = [('name', '=', self.builder_form_a_v1.name)]

        # form_a has already 2 versions, created from TestOrbeonCommon.setUp()
        self.assertEquals(self.builder_model.search_count(name_filter), 2)

        # version 1, 2: just check
        version_1_filter = list(name_filter)
        version_1_filter.append(('version', '=', 1))

        builder_version_1 = self.builder_model.search(version_1_filter)

        self.assertEquals(builder_version_1.version, 1)
        self.assertEquals(builder_version_1.state, orbeon_builder.STATE_NEW)
        self.assertEquals(self.builder_model.search_count(version_1_filter), 1)

        # version 2: initial to be copied
        current_version_filter = list(name_filter)
        current_version_filter.append(('state', '=', orbeon_builder.STATE_CURRENT))
        builder_current = self.builder_model.search(current_version_filter)

        self.assertEquals(builder_current.version, 2)
        self.assertEquals(builder_current.state, orbeon_builder.STATE_CURRENT)
        self.assertEquals(self.builder_model.search_count(current_version_filter), 1)

        # version 3: COPY from builder_current (builder_form_a_v2_current)
        self.builder_form_a_v2_current.new_version_builder_form()

        version_3_filter = list(name_filter)
        version_3_filter.append(('version', '=', 3))
        builder_version_3 = self.builder_model.search(version_3_filter)

        self.assertEquals(builder_version_3.version, 3)
        self.assertEquals(builder_version_3.state, orbeon_builder.STATE_NEW)
        self.assertEquals(self.builder_model.search_count(version_3_filter), 1)
        self.assertEquals(self.builder_model.search_count(name_filter), 3)

        # version 4: COPY from builder_version_1 (builder_form_a_v1)
        builder_version_3.new_version_builder_form()

        version_4_filter = list(name_filter)
        version_4_filter.append(('version', '=', 4))
        builder_version_4 = self.builder_model.search(version_4_filter)

        self.assertEquals(builder_version_4.version, 4)
        self.assertEquals(builder_version_4.state, orbeon_builder.STATE_NEW)
        self.assertEquals(self.builder_model.search_count(version_4_filter), 1)
        self.assertEquals(self.builder_model.search_count(name_filter), 4)

        # version 5: COPY from builder_current (builder_form_a_v2_current)
        builder_version_4.new_version_builder_form()

        version_5_filter = list(name_filter)
        version_5_filter.append(('version', '=', 5))
        builder_version_5 = self.builder_model.search(version_5_filter)

        self.assertEquals(builder_version_5.version, 5)
        self.assertEquals(builder_version_5.state, orbeon_builder.STATE_NEW)
        self.assertEquals(self.builder_model.search_count(version_5_filter), 1)
        self.assertEquals(self.builder_model.search_count(name_filter), 5)

        # version 6: copy from builder_version_4 (new_versioned/create above)
        builder_version_5.new_version_builder_form()

        version_6_filter = list(name_filter)
        version_6_filter.append(('version', '=', 6))
        builder_version_6 = self.builder_model.search(version_6_filter)

        self.assertEquals(builder_version_6.version, 6)
        self.assertEquals(builder_version_6.state, orbeon_builder.STATE_NEW)
        self.assertEquals(self.builder_model.search_count(version_6_filter), 1)
        self.assertEquals(self.builder_model.search_count(name_filter), 6)

        # Only 1 version where state is 'current'
        state_current_filter = list(name_filter)
        state_current_filter.append(('state', '=', orbeon_builder.STATE_CURRENT))

        self.assertEquals(self.builder_model.search_count(state_current_filter), 1)

        # 5 versions where state is 'new'
        state_new_filter = list(name_filter)
        state_new_filter.append(('state', '=', orbeon_builder.STATE_NEW))

        self.assertEquals(self.builder_model.search_count(state_new_filter), 5)

    def test_url_is_readonly(self):
        """Test url field is readonly"""
        field = self.builder_model._fields['url']
        self.assertTrue(field.readonly)

    def test_url_edit_state(self):
        """Test edit URL (function field)"""
        builder_1_url = "%s/fr/orbeon/builder/edit/%i" % (self.server_1.url, self.builder_form_a_v1.id)

        self.assertEquals(self.builder_form_a_v1.state, orbeon_builder.STATE_NEW)
        self.assertEquals(self.builder_form_a_v1.url, builder_1_url)

    def test_url_view_state(self):
        """Test view URL (function field)"""
        builder_2_url = "%s/fr/orbeon/builder/view/%i" % (self.server_1.url, self.builder_form_a_v2_current.id)

        self.assertEquals(self.builder_form_a_v2_current.state, orbeon_builder.STATE_CURRENT)
        self.assertEquals(self.builder_form_a_v2_current.url, builder_2_url)
