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

from orbeon_xml_api import builder, runner, controls
from odoo import models

import logging

_logger = logging.getLogger(__name__)


class OrbeonRunner(models.Model):
    _name = 'orbeon.runner'
    _inherit = ['orbeon.runner']

    def __getattr__(self, name):
        if name == 'o_xml':
            if 'o_xml' not in self.__dict__:
                lang = 'en'
                controls = {
                    'ImageAnnotationControl': ImageAnnotationControlOdoo,
                    # 'AnyUriControl': AnyUriControlOdoo
                }
                builder_obj = builder.Builder(self.builder_id.xml, lang, controls=controls)
                self.o_xml = runner.Runner(self.xml, builder_obj)
            return self.o_xml
        else:
            return self.__getattribute__(name)


class ImageAnnotationControlOdoo(controls.ImageAnnotationControl):

    def init_runner_form_attrs(self, runner_element):
        decoded = self.decode(runner_element)

        if decoded:
            self.image = decoded['image']
            self.annotation = decoded['annotation']

    def decode(self, element):
        data = {
            'image': None,
            'annotation': None
        }

        if element is None:
            return data

        for el in element.getchildren():
            if el.tag == 'annotation':
                data['annotation'] = el.text
            elif el.tag == 'image':
                data['image'] = el.text

        return data


class AnyUriControlOdoo(controls.AnyUriControl):

    def decode(self, element):
        res = {}

        if element is None:
            return res

        for el in element.getchildren():
            res[el.tag] = {el.tag: "%s FROM %s" % (el.tag, self.__class__.__name__)}

        return res
