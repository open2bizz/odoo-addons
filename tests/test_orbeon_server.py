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
from odoo.exceptions import ValidationError

from test_orbeon_common import TestOrbeonCommon, TODO

from psycopg2 import IntegrityError
import logging

_logger = logging.getLogger(__name__)

class TestOrbeonServer(TestOrbeonCommon):
    """Tests for Orbeon Server"""
    
    def test_create_missing_required_name(self):
        """Test create with missing, but required, name"""
        with self.assertRaisesRegexp(IntegrityError, 'column "name" violates not-null'):
            self.server_model.sudo().create(
                {
                    'base_url': 'http://localhost/orbeon_test_server_2',
                    'default_builder_xml': self.server_1.default_builder_xml
                }
            )

    def test_write_missing_required_name(self):
        """Test write with missing, but required, name"""
        with self.assertRaisesRegexp(IntegrityError, 'column "name" violates not-null'):
            self.server_model.sudo().create(
                {
                    'base_url': 'http://localhost/orbeon_test_server_2',
                    'default_builder_xml': self.server_1.default_builder_xml
                }
            )

    def test_create_missing_required_base_url(self):
        """Test create with missing, but required, base_url"""
        with self.assertRaisesRegexp(IntegrityError, 'column "base_url" violates not-null'):
            self.server_model.sudo().create(
                {
                    'name': 'Test Server',
                    'default_builder_xml': self.server_1.default_builder_xml
                }
            )

    def test_write_missing_required_base_url(self):
        """Test write with missing, but required, base_url"""
        with self.assertRaisesRegexp(IntegrityError, 'column "base_url" violates not-null'):
            self.server_model.sudo().create(
                {
                    'name': 'Test Server',
                    'default_builder_xml': self.server_1.default_builder_xml
                }
            )

    def test_create_missing_required_default_builder_xml(self):
        """Test create with missing, but required, default_builder_xml"""
        with self.assertRaisesRegexp(IntegrityError, 'column "default_builder_xml" violates not-null'):
            self.server_model.sudo().create(
                {
                    'name': 'Test Server',
                    'base_url': 'http://localhost/orbeon_test_server_2',
                }
            )

    def test_write_missing_required_default_builder_xml(self):
        """Test write with missing, but required, default_builder_xml"""
        with self.assertRaisesRegexp(IntegrityError, 'column "default_builder_xml" violates not-null'):
            self.server_model.sudo().create(
                {
                    'name': 'Test Server',
                    'base_url': 'http://localhost/orbeon_test_server_2',
                }
            )

    def test_create_successful(self):
        """Test succesful create"""
        try:
            self.server_model.sudo().create(
                {
                    'name': 'Test Server',
                    'base_url': 'http://localhost/orbeon_test_server_2',
                    'default_builder_xml': self.server_1.default_builder_xml
                }
            )
        except Exception:
            self.fail("create() raised an Exception unexpectedly!")

    def test_create_constraint_unique_name(self):
        """Test create with duplicate name, in existing server"""

        # Check whether 'name' of the comparison server-object is valid.
        self.assertEquals(self.server_1.name, 'server_1')

        with self.assertRaisesRegexp(ValidationError, 'Server with name .* already exists'):
            self.server_model.sudo().create(
                {
                    'name': 'server_1',
                    'base_url': 'http://localhost/server_test_create_constraint_unique_name',
                    'default_builder_xml': self.xmlFromFile('test_orbeon4.10_builder_default.xml')
                }
            )

    def test_write_constraint_unique_name(self):
        """Test write with duplicate name, in existing server"""

        # First create 2nd server
        try:
            record = self.server_model.sudo().create(
                {
                    'name': 'server_test_write_constraint_unique_name',
                    'base_url': 'http://localhost/server_test_write_constraint_unique_name',
                    'default_builder_xml': self.xmlFromFile('test_orbeon4.10_builder_default.xml')
                }
            )
        except Exception as e:
            self.fail(e)
        
        with self.assertRaisesRegexp(ValidationError, 'Server with name .* already exists'):
            self.server_1.sudo().write(
                {
                    'name': 'server_test_write_constraint_unique_name'
                }
            )

    def test_create_constraint_unique_base_url(self):
        """Test write with duplicate base_url, in existing server"""

        # Check whether 'name' of the comparison server-object is valid.
        self.assertEquals(self.server_1.base_url, 'http://localhost/orbeon_server_1')

        with self.assertRaisesRegexp(ValidationError, 'Server with URL .* already exists'):
            self.server_model.sudo().create(
                {
                    'name': 'test_create_constraint_unique_base_url_server',
                    'base_url': 'http://localhost/orbeon_server_1',
                    'default_builder_xml': self.xmlFromFile('test_orbeon4.10_builder_default.xml')
                }
            )

    def test_write_constraint_unique_base_url(self):
        """Test write with duplicate base_url, in existing server"""

        # First create 2nd server
        try:
            record = self.server_model.sudo().create(
                {
                    'name': 'server_test_write_constraint_unique_name',
                    'base_url': 'http://localhost/server_test_write_constraint_unique_base_url',
                    'default_builder_xml': self.xmlFromFile('test_orbeon4.10_builder_default.xml')
                }
            )
        except Exception as e:
            self.fail(e)
        
        with self.assertRaisesRegexp(ValidationError, 'Server with URL .* already exists'):
            self.server_1.sudo().write(
                {
                    'base_url': 'http://localhost/server_test_write_constraint_unique_base_url',
                }
            )

    @TODO
    def test_write_successful(self):
        """Test successful write"""

    @TODO
    def test_delete_contains_builder_forms(self):
        """Test delete with references to orbeon.builder(forms)"""        

    def test_summary_url(self):
        """Test summary_url (function field)"""
        summary_url = "%s/fr/orbeon/builder/summary" % self.server_1.base_url
        msg = "Expect summary_url to be %s ! Check function: orbeon_server_summary_url()" % summary_url

        self.assertEquals(self.server_1.summary_url, summary_url)
