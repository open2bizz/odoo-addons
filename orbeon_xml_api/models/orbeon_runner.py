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
from odoo.exceptions import UserError

from lxml import etree

import logging

_logger = logging.getLogger(__name__)


class OrbeonRunner(models.Model):
    _name = 'orbeon.runner'
    _inherit = ['orbeon.runner']

    def __getattr__(self, name):
        if name == 'o_xml':
            if 'o_xml' not in self.__dict__:
                context = self._context
                if 'lang' in context:
                    lang = context['lang']
                elif 'lang' not in context and 'uid' in context:
                    lang = self.env['res.users'].browse(context['uid']).lang
                elif 'lang' not in context and 'uid' not in context:
                    lang = self.env['res.users'].browse(self.write_uid).lang
                else:
                    raise UserError("The form can't be loaded. No (user) language was set.")

                res_lang = self.env['res.lang'].search([('code', '=', lang)], limit=1)

                controls = {
                    'ImageAnnotationControl': ImageAnnotationControlOdoo,
                    'AnyUriControl': AnyUriControlOdoo
                }

                builder_xml = u'%s' % self.builder_id.xml
                builder_xml = bytes(bytearray(builder_xml, encoding='utf-8'))

                builder_obj = builder.Builder(
                    builder_xml, res_lang.iso_code,
                    controls=controls, context={'model_object': self}
                )

                runner_xml = u'%s' % self.xml
                runner_xml = bytes(bytearray(runner_xml, encoding='utf-8'))

                if self.xml is False:
                    # HACK masquerade empty Runner object on the o_xml attr.
                    self.o_xml = EmptyRunner(runner_xml, builder_obj)
                else:
                    self.o_xml = runner.Runner(runner_xml, builder_obj)
            return self.o_xml
        else:
            return self.__getattribute__(name)


#####################################################
# Overrides/subclasses for "orbeon-xml-api" Controls.
#####################################################


class ImageAnnotationControlOdoo(controls.ImageAnnotationControl):

    def init_runner_form_attrs(self, runner_element):
        decoded = self.decode(runner_element)

        if decoded:
            self.image = decoded['image']
            self.annotation = decoded['annotation']
            self.value = decoded['annotation']

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
        res = super(AnyUriControlOdoo, self).decode(element)
        uri = res.get('uri', False)

        if not uri or not isinstance(uri, basestring):
            return res

        # Whereby the last path-component shall be the ir.attachment (file)name.
        comps = uri.split('/')

        attach_model = self._builder.context['model_object'].env['ir.attachment']
        attach_obj = attach_model.search([('name', '=', comps[-1])], limit=1)

        res['value'] = "%s%s" % ('data:image/jpeg;base64,', attach_obj.datas)

        return res

###################################################
# Empty "orbeon-xml-api" alike objects.
# REASON: In case the 'orbeon.runner' xml is empty.
###################################################


class EmptyRunner(runner.Runner):

    def set_xml_root(self):
        self.xml_root = etree.Element('empty')

    def init(self):
        self.form = EmptyRunnerForm(self)

        for name, control in self.builder.controls.items():
            self.controls[name] = EmptyControl(self.builder, control._bind, False)


class EmptyControl(controls.Control):

    def __getattr__(self, name):
        if name == 'label':
            return self.label
        else:
            return ''

    def set_default_raw_value(self):
        self.default_raw_value = getattr(self._model_instance, 'text', None)

    def set_default_value(self):
        self.default_value = self.decode(self._model_instance)

    def set_raw_value(self):
        self._raw_value = ''

    def decode(self, element):
        return ''

    def encode(self, value):
        return value


class EmptyRunnerForm:

    def __init__(self, runner):
        self._runner = runner

    def __getattr__(self, s_name):
        name = self._runner.builder.sanitized_control_names.get(s_name, False)
        if name:
            return self._runner.get_form_control(name)
        else:
            return False
