# -*- coding: utf-8 -*-
##############################################################################
#
#    open2bizz
#    Copyright (C) 2017 open2bizz (open2bizz.nl).
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

from orbeon_xml_api.runner import Runner, RunnerForm
from odoo.addons.orbeon.tests.test_orbeon_common import TestOrbeonCommon

from datetime import datetime
import logging

_logger = logging.getLogger(__name__)


class TestOrbeonRunnerXmlApi(TestOrbeonCommon):
    """Tests for Orbeon Runner XML API"""

    def test_o_xml_is_runner_api(self):
        self.assertIsInstance(self.runner_form_a_v2.with_context(uid=1).o_xml, Runner)
        self.assertIsInstance(self.runner_form_a_v2.with_context(uid=1).o_xml.form, RunnerForm)

    def test_o_xml_runner_api_get(self):
        self.assertEqual(self.runner_form_a_v2.with_context(uid=1).o_xml.form.inputcontrol1.value, 'text 1')
        self.assertEqual(self.runner_form_a_v2.with_context(uid=1).o_xml.form.inputcontrol2.value, 'text 2')

        date_obj = datetime.strptime('2016-05-11', '%Y-%m-%d').date()
        self.assertEqual(self.runner_form_a_v2.with_context(uid=1).o_xml.form.datecontrol1.value, date_obj)
