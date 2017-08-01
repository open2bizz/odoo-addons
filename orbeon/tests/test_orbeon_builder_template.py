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

from ..models import orbeon_builder_template

from psycopg2 import IntegrityError
from lxml import etree

import logging

_logger = logging.getLogger(__name__)


class TestOrbeonBuilderTemplate(TestOrbeonCommon):
    """Tests for Orbeon Builder Template Forms"""

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
                self.builder_template_model.sudo().create(
                    {
                        'form_name': name,
                    }
                )
