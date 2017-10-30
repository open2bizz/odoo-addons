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
from odoo import fields, models

import logging
import os

from lxml import etree
from xmlunittest import XmlTestCase

from ..models import orbeon_server
from ..models import orbeon_builder
from ..models import orbeon_runner

_logger = logging.getLogger(__name__)


class TestOrbeonCommon(TransactionCase, XmlTestCase):
    """Common utilities for Orbeon Tests"""
    
    def setUp(self):
        super(TestOrbeonCommon, self).setUp()

        # Because we validate xml
        self.maxDiff = None

        self.server_model = self.env['orbeon.server']
        self.builder_model = self.env['orbeon.builder']
        self.builder_template_model = self.env['orbeon.builder.template']
        self.runner_model = self.env['orbeon.runner']

        # server_1
        self.server_1 = self.server_model.sudo().create(
            {
                'name': 'server_1',
                'url': 'http://localhost/orbeon_server_1',
                'persistence_server_port': '10111',
                'persistence_server_processtype': orbeon_server.PERSISTENCE_SERVER_SINGLE_THREADED,
                'builder_templates_created': True
            }
        )

        self.builder_template_form_1 = self.builder_template_model.sudo().create(
            {
                'server_id': self.server_1.id,
                'module_id': self.env['ir.model.data'].xmlid_to_res_id('base.orbeon'),
                'form_name': 'form_a',
                'xml': self.xmlFromFile('test_orbeon4.10_builder_default.xml'),
                'fetched_from_orbeon': False
            }
        )

        self.builder_form_a_v1 = self.builder_model.sudo().create(
            {
                'name': 'form_a',
                'title': 'Form A',
                # state: orbeon_builder.STATE_NEW
                # version: 1
                'version_comment': '1 input',
                'server_id': self.server_1.id,
                'builder_template_id': self.builder_template_form_1.id
            }
        )

        # With parent_id
        self.builder_form_a_v2_current = self.builder_model.sudo().create(
            {
                'name': 'form_a',
                'parent_id': self.builder_form_a_v1.id,
                'title': 'Form A',
                'state': orbeon_builder.STATE_CURRENT,  # live (in production)
                'version': 2,
                'version_comment': '2 inputs, 1 date',
                'server_id': self.server_1.id,
                'builder_template_id': self.builder_template_form_1.id
            }
        )

        self.builder_form_a_v2_current.write(
            {
                'xml': self.xmlFromFile('test_orbeon4.10_builder_form_a_v2.xml'),
            })

        self.builder_form_b_no_runner_forms = self.builder_model.sudo().create(
            {
                'name': 'form_b',
                'title': 'Form B',
                'state': orbeon_builder.STATE_CURRENT,  # live (in production)
                'version': 1,
                'version_comment': 'no runner forms, just/only a builder form',
                'server_id': self.server_1.id,
                'builder_template_id': self.builder_template_form_1.id
            }
        )

        res_model_id = self.env['ir.model'].search([('model', '=', 'res.users')], limit=1)

        self.builder_form_c_erp_fields_v1 = self.builder_model.sudo().create(
            {
                'name': 'form_c_erp_fields',
                'title': 'Form C ERP fields',
                'state': orbeon_builder.STATE_CURRENT,  # live (in production)
                'version': 1,
                'version_comment': "ERP fields res_user model: name, login, image",
                'server_id': self.server_1.id,
                'res_model_id': res_model_id.id,
                'builder_template_id': self.builder_template_form_1.id
            }
        )

        self.builder_form_c_erp_fields_v1.write(
            {
                'xml': self.xmlFromFile('test_orbeon4.10_builder_form_c_erp_fields_v1.xml'),
            }
        )

        # Assume newly created form by Odoo
        self.runner_form_a_v1_new = self.runner_model.sudo().create(
            {
                'builder_id': self.builder_form_a_v1.id,
            }
        )

        # Assume newly created form by Odoo
        self.runner_form_a_v2_new = self.runner_model.sudo().create(
            {
                'builder_id': self.builder_form_a_v2_current.id,
            }
        )

        # Assume already form stored (PUT) by Orbeon
        self.runner_form_a_v1 = self.runner_model.sudo().create(
            {
                'builder_id': self.builder_form_a_v1.id,
                'xml': self.xmlFromFile('test_orbeon4.10_runner_form_a_v1.xml'),
            }
        )

        # Assume already form stored (PUT) by Orbeon
        self.runner_form_a_v2 = self.runner_model.sudo().create(
            {
                'builder_id': self.builder_form_a_v2_current.id,
                'xml': self.xmlFromFile('test_orbeon4.10_runner_form_a_v2.xml'),
            }
        )

        self.user_1 = self.env['res.users'].browse(1)

        self.runner_form_c_erp_fields_v1 = self.runner_model.sudo().create(
            {
                'builder_id': self.builder_form_c_erp_fields_v1.id,
                'res_id': self.user_1.id
            }
        )

    def xmlFromFile(self, filename):
        cwd = os.path.dirname(os.path.realpath(__file__))
        return etree.tostring(etree.parse("%s/data/%s" % (cwd, filename)))

    """
    Overrides xmlunittest to check on empty result of by xpath
    """
    def assertXpathValues(self, node, xpath, values, default_ns_prefix='ns'):
        """Asserts each xpath's value is in the expected values."""
        super(TestOrbeonCommon, self).assertXpathValues(node, xpath, values, default_ns_prefix)
        
        expression = self.build_xpath_expression(node, xpath, default_ns_prefix)
        results = expression.evaluate(node)

        if len(results) == 0 and len(values) > 0:
            self.fail('No value found for node %s\n'
                      'XPath: %s\n'
                      'Expected values: %s\n'
                      'Element:\n%s'
                      % (node.tag, xpath,
                         ', '.join(values),
                         etree.tostring(node, encoding='unicode', pretty_print=True)))
