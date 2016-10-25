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
from openerp.tests.common import TransactionCase

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

    @TODO
    def test_create_constraint_unique_name(self):
        """Test create with duplicate name, in existing server"""

    @TODO
    def test_write_constraint_unique_name(self):
        """Test write with duplicate name, in existing server"""

    @TODO
    def test_create_constraint_unique_base_url(self):
        """Test write with duplicate base_url, in existing server"""

    @TODO
    def test_write_constraint_unique_base_url(self):
        """Test write with duplicate base_url, in existing server"""

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
