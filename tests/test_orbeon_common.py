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

import logging
import os

from lxml import etree
from xmlunittest import XmlTestMixin

try:
    from ...test_extensions import TODO
except:
    def TODO(self):
        pass

from ..models import orbeon_builder
from ..models import orbeon_runner

_logger = logging.getLogger(__name__)

class TestOrbeonCommon(TransactionCase, XmlTestMixin):
    """Common utilities for Orbeon Tests"""
    
    def setUp(self):
        super(TestOrbeonCommon, self).setUp()

        # Because we validate xml
        self.maxDiff = None

        self.server_model = self.env['orbeon.server']
        self.builder_model = self.env['orbeon.builder']
        self.runner_model = self.env['orbeon.runner']

        # server_1
        self.server_1 = self.server_model.sudo().create(
            {
                'name': 'server_1',
                'url': 'http://localhost/orbeon_server_1',
                'default_builder_xml': self.xmlFromFile('test_orbeon4.10_builder_default.xml')
            }
        )

        # builder_1 (version 1): xml = default_builder_xml
        self.builder_form_a_v1 = self.builder_model.sudo().create(
            {
                'name': 'form_a',
                'title': 'Form A',
                # state: orbeon_builder.STATE_NEW
                # version: 1
                'version_comment': '1 input',
                'server_id': self.server_1.id,
            }
        )

        self.builder_form_a_v2_current = self.builder_model.sudo().create(
            {
                'name': 'form_a',
                'title': 'Form A',
                'state': orbeon_builder.STATE_CURRENT, # live (in production)
                'version': 2,
                'version_comment': '2 inputs, 1 date',
                'server_id': self.server_1.id,
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
                'state': orbeon_builder.STATE_CURRENT, # live (in production)
                'version': 1,
                'version_comment': 'no runner forms, just/only a builder form',
                'server_id': self.server_1.id,
            }
        )

        # self.builder_form_a_v3_new_all = self.builder_model.sudo().create(
        #     {
        #         'name': 'form_a',
        #         'state': orbeon_builder.STATE_NEW,
        #         'version': 3,
        #         'version_comment': 'Several controls; also with Odoo directives: nocopy (NC.), ERP-fields',
        #         'xml': self.xmlFromFile('test_orbeon4.10_builder_form_a_v3_all.xml'),
        #         'server_id': self.server_1.id,
        #     }
        # )

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

        # self.runner_form_a_v3_all = self.runner_model.sudo().create(
        #     {
        #         'builder_id': self.builder_form_a_v1.id,
        #         'xml': self.xmlFromFile('test_orbeon4.10_runner_form_a_v2_all.xml'),
        #     }
        # )

    def xmlFromFile(self, filename):
        cwd = os.path.dirname(os.path.realpath(__file__))
        return etree.tostring(etree.parse("%s/data/%s" % (cwd, filename)))
