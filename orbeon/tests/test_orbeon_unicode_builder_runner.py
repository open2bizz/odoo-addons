# -*- coding: utf-8 -*-
##############################################################################
#
#    open2bizz
#    Copyright (C) 2016,2017 open2bizz (open2bizz.nl).
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
from lxml import etree
import logging

from test_orbeon_common import TestOrbeonCommon


_logger = logging.getLogger(__name__)


class TestOrbeonUnicodeBuilderRunner(TestOrbeonCommon):
    """Tests for Orbeon Builder Forms"""

    def setUp(self):
        super(TestOrbeonUnicodeBuilderRunner, self).setUp()

        self.unicode_form_name = 'form_unicode'
        self.unicode_form_title = 'Form Unicode'

    def _create_builder_unicode(self):
        xml = self.xmlFromFile('test_orbeon4.10_builder_form_unicode.xml')

        """Test Builder create with Unicode"""
        builder = self.builder_model.sudo().create(
            {
                'name': self.unicode_form_name,
                'title': self.unicode_form_title,
                'version_comment': 'Form with Unicode chars',
                'server_id': self.server_1.id,
                'xml': xml,
            }
        )

        return builder

    def test_unicode_builder_create(self):
        """Test Builder create with Unicode"""
        try:
            self._create_builder_unicode()
        except Exception as e:
            self.fail(e)

    def test_unicode_builder_write(self):
        """Test Builder write with Unicode"""
        try:
            self.builder_form_a_v1.sudo().write(
                {
                    'xml': self.xmlFromFile('test_orbeon4.10_builder_form_unicode.xml')
                }
            )
        except Exception as e:
            self.fail(e)

    def test_unicode_builder_copy_as_new_version(self):
        """Test Builder with Unicode, copy as new version"""
        builder = self._create_builder_unicode()

        try:
            new_builder = builder.copy_as_new_version()
            self.assertEqual(new_builder.version, 2)
            self.assertXmlDocument(new_builder.xml)
        except Exception as e:
            self.fail(e)

    def test_unicode_builder_orbeon_search_read(self):
        """Test Builder orbeon_search_read with Unicode"""
        builder = self._create_builder_unicode()
        domain = [('id', '=', builder.id)]

        try:
            res = self.builder_model.sudo().orbeon_search_read_data(domain, ['xml'])
            self.assertXmlDocument(res['xml'])
        except Exception as e:
            self.fail(e)

    def test_unicode_runner_create(self):
        """Test Runner create with Unicode"""
        builder = self._create_builder_unicode()

        try:
            self.runner_model.sudo().create(
                {
                    'builder_id': builder.id
                }
            )
        except Exception as e:
            self.fail(e)

    def test_unicode_runner_read_and_write(self):
        """Test Runner write with Unicode"""

        runner = self.runner_form_a_v1.sudo().write(
            {
                'xml': self.xmlFromFile('test_orbeon4.10_runner_form_unicode.xml')
            }
        )

        domain = [('id', '=', self.runner_form_a_v1.id)]
        runner = self.runner_model.orbeon_search_read_data(domain, ['xml'])

        xml = runner['xml']

        # Fix Unicode parser (ValueError)
        parser = etree.XMLParser(ns_clean=True, recover=True, encoding='utf-8')
        root = etree.XML(xml.decode('utf-8'), parser)
        xml = etree.tostring(root, encoding='unicode')

        root = self.assertXmlDocument(xml)
        self.assertXpathValues(root, '//input-control-2/text()', [u'continuüm and élite'])
