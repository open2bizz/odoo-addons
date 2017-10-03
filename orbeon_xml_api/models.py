# -*- encoding: utf-8 -*-
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

from orbeon_xml_api.runner import Runner
from odoo import models

import logging

_logger = logging.getLogger(__name__)


class OrbeonRunner(models.Model):
    _name = 'orbeon.runner'
    _inherit = ['orbeon.runner']

    def __getattr__(self, name):
        if name == 'o_xml':
            if 'o_xml' not in self.__dict__:
                # runner = Runner(self.xml, None, self.builder_id.xml)
                # self.o_xml = runner.form
                self.o_xml = Runner(self.xml, None, self.builder_id.xml)
            return self.o_xml
        else:
            # return self.__getattribute__(name)
            return self.__getattribute__(name)
