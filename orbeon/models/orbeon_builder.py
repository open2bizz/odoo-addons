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
from odoo import models, fields, api
from odoo.exceptions import ValidationError

from lxml import etree

import re

import logging
_logger = logging.getLogger(__name__)

STATE_CURRENT = 'current'
STATE_NEW = 'new'
STATE_OBSOLETE = 'obsolete'


class OrbeonBuilder(models.Model):
    _name = "orbeon.builder"
    _order = 'res_model_id DESC, name ASC, version ASC'

    name = fields.Char(
        "Name",
        required=True,
        help="""
        Identifies this specific form (e.g. "health-record" or "claim").
        This name can be used in APIs, so we recommend you use only lowercases characters.""",
    )

    title = fields.Char(
        "Title",
        help="Form title in the current language",
        default="Untitled Form"
    )

    description = fields.Text(
        "Description",
        help="Form description in the current language")

    version = fields.Integer(
        "Version",
        required=True,
        readonly=True,
        default=1)

    version_comment = fields.Text(
        "Version Comment",
        required=True)

    state = fields.Selection(
        [
            (STATE_NEW, "New"),
            (STATE_CURRENT, "Current"),
            (STATE_OBSOLETE, "Obsolete"),
        ],
        "State",
        default=STATE_NEW,
        required=True,
        help="""\
        - New: In draft and was never published (Current)
        - Current: Published i.e. live
        - Obsolete: Was published but obsolete"""
    )

    xml = fields.Text(
        'XML')

    server_id = fields.Many2one(
        "orbeon.server",
        "Server",
        required=True,
        ondelete='restrict')

    builder_template_id = fields.Many2one(
        "orbeon.builder.template",
        "Builder Form Template",
        ondelete='set null',
        help="By default some Builder Form Templates are shipped by the Orbeon Server."
    )

    runner_form_ids = fields.One2many(
        "orbeon.runner",
        "builder_id",
        string="Form runners")

    res_model_id = fields.Many2one(
        "ir.model",
        "Resource Model",
        ondelete='restrict',
        help="Model as resource this form represents or acts on"
    )

    url = fields.Text(
        'URL',
        compute="_get_url",
        readonly=True)

    @api.one
    @api.constrains('name')
    def constaint_check_name(self):
        """
        Validate name according to the RFC3986 Path (Section 3.3) section
        """
        if re.search(r"\?|\#|\/|:", self.name):
            raise ValidationError('Name should not contain following characters: question mark ("?"), '
                                  'pound ("#"), slash ("/"), colon (":")?')

    @api.one
    @api.constrains("name", "state")
    def constraint_one_current(self):
        """Per name there can be only 1 record with
        state current at a time.
        """
        cur_record = self.search([
            ("name", "=", self.name),
            ("state", "=", STATE_CURRENT)
            ])
        if len(cur_record) > 1:
            raise ValidationError("%s already has a record with status 'current'.\
                    Only one builder form can be current at a time." % self.name)

    @api.one
    @api.constrains("name", "version")
    def constraint_one_version(self):
        """Per name there can be only 1 record with
        same version at a time.
        """

        domain = [('name', '=', self.name)]
        name_version_grouped = self.read_group(domain, ['version'], ['version'])

        if name_version_grouped[0]['version_count'] > 1:
            raise ValidationError("%s already has a record with version: %d"
                                  % (self.name, self.version))

    @api.model
    def create(self, vals):
        if 'server_id' in vals:
            template = self.env['orbeon.builder.template'].browse(vals['builder_template_id'])
            xml = etree.fromstring(template.xml)

            if len(xml.xpath('//application-name')) > 0:
                xml.xpath('//application-name')[0].text = 'odoo'

            if 'name' in vals and len(xml.xpath('//form-name')) > 0:
                xml.xpath('//form-name')[0].text = vals['name']

            if 'title' in vals and vals['title']:
                xml.xpath('//metadata/title')[0].text = vals['title']

                if len(xml.xpath('//title')) > 0:
                    xml.xpath('//title')[0].text = vals['title']

                if len(xml.xpath('//xh:title', namespaces={'xh': "http://www.w3.org/1999/xhtml"})) > 0:
                    xml.xpath('//xh:title', namespaces={'xh': "http://www.w3.org/1999/xhtml"})[0].text = vals['title']

            vals['xml'] = etree.tostring(xml)

        res = super(OrbeonBuilder, self).create(vals)

        return res

    @api.one
    @api.returns('self', lambda value: value)
    def copy_as_new_version(self):
        # Get last version for builder-forms by name
        builder = self.search([('name', '=', self.name)], limit=1, order='version DESC')

        alter = {}
        alter["state"] = STATE_NEW
        alter["version"] = builder.version + 1
        res = super(OrbeonBuilder, self).copy(alter)

        return res

    @api.multi
    def new_version_builder_form(self):
        res = self.copy_as_new_version()

        form_view = self.env["ir.ui.view"].search(
            [("name", "=", "orbeon.builder_form.form")]
        )[0]

        tree_view = self.env["ir.ui.view"].search(
            [("name", "=", "orbeon.builder_form.tree")]
        )[0]

        return {
            "name": self.name,
            "type": "ir.actions.act_window",
            "res_model": "orbeon.builder",
            "view_type": "form",
            "view_mode": "form, tree",
            "views": [
                [form_view.id, "form"],
                [tree_view.id, "tree"],
            ],
            "target": "current",
            "res_id": res.id,
            "context": {}
        }

    @api.multi
    def open_orbeon_builder_form(self):
        return {
            "name": 'Orbeon',
            "type": "ir.actions.act_url",
            "target": "new",
            'url': self.url
        }

    @api.onchange('state', 'server_id')
    def _get_url(self):
        if hasattr(self, '_origin') and not isinstance(self._origin.id, models.NewId):
            builder_id = self._origin.id
        else:
            builder_id = self.id

        builder_url = "%s/%s" % (self.server_id.url, "fr/orbeon/builder")
        get_mode = {STATE_NEW: 'edit'}
        url = "%s/%s/%i" % (builder_url, get_mode.get(self.state, 'view'), builder_id)

        self.url = url

    @api.model
    def orbeon_search_read_data(self, domain=None, fields=None):
        builder = self.search(domain or [], limit=1)

        res = {'id': builder['id']}

        for f in fields:
            res[f] = builder[f]

        return res

    @api.one
    def get_xml_form_node(self):
        parser = etree.XMLParser(ns_clean=True, encoding='utf-8')

        # Cast to string, to prevent Unicode error!
        root = etree.XML(self.xml.encode('utf-8'), parser)

        form_node = root.xpath(
            "//xf:instance[@id='fr-form-instance']/form",
            namespaces={'xf': "http://www.w3.org/2002/xforms"}
        )[0]

        form = etree.XML(etree.tostring(form_node), parser)
        etree.cleanup_namespaces(form)

        return etree.tostring(form)