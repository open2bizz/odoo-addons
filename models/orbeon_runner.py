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
from openerp import models, fields, api

import logging

_logger = logging.getLogger(__name__)

class orbeon_runner(models.Model):
    _name = "orbeon.runner"
    
    builder_id = fields.Many2one(
        "orbeon.builder",
        string="Form builder")

    builder_name = fields.Char(
        "Builder name",
        compute="_get_builder_name",
        readonly=True)

    builder_version = fields.Integer(
        "Builder version",
        compute="_get_builder_version",
        readonly=True)
    
    state = fields.Selection(
        [
            ("new", "New"),
            ("progress", "In Progress"),
            ("complete", "Complete"),
            ("canceled", "Canceled"),
        ],
        string="State",
        default="new")

    """Lets us know if this filed is merged with latest builder fields."""
    is_merged = fields.Boolean(
        'Is Merged',
        default=False)

    xml = fields.Text(
        'XML',
        default=None) # WTF! Odoo ORM decodes NULL to False instead of None.

    url = fields.Text(
        'URL',
        compute="_get_url",
        readonly=True)

    @api.one
    def _get_builder_name(self, id=None):
        self.builder_name = self.builder_id.name

    @api.one
    def _get_builder_version(self, id=None):
        self.builder_version = self.builder_id.version
    
    @api.one
    def _get_url(self, id=None):
        server_url = self.builder_id.server_id.base_url
        base_path = 'fr/orbeon/runner'
        base_url = "%s/%s" % (server_url, base_path)
        
        if isinstance(self.id, models.NewId):
            url = "%s/new" % base_url
        else:
            get_mode = {'new': 'edit', 'progress': 'edit'}
            path_mode = get_mode.get(self.state ,'view')
            url = "%s/%s/%i" % (base_url, path_mode, self.id)
            self.url = url

    @api.multi
    def action_open_orbeon_runner(self):
        self.ensure_one()
        return {
            'name': 'Orbeon',
            'type': 'ir.actions.act_url',
            'target': 'new',
            'url': self.url
        }

    def orbeon_runner_form(self, cr, uid, ids, context=None):
        _logger.error('open orbeon_runner_form')
        # TODO From here open wizard (action window: to coppy or create/new

    @api.multi
    def write(self, vals):
        if self.is_merged == False:
            vals['is_merged'] = True
        
        res = super(orbeon_runner, self).write(vals)
        return res
    @api.multi
    def duplicate_runner_form(self):
        alter = {}
        alter["state"] = 'new'
        alter["is_merged"] = False

        # XXX maybe useless if merge_xml_current_builder() returns None?
        alter["xml"] = self.merge_xml_current_builder()

        res = super(orbeon_runner, self).copy(alter)        
        
    # TODO: check whether and which @api decorator is needed here
    def merge_xml_current_builder(self):
        # No merge required if the runner's builder already is currrent
        if (self.builder_id.state == 'current'):
            return self.xml

        orbeon_server = self.env['orbeon.builder']
        current_builder = orbeon_server.search(
            [('name', '=', self.builder_id.name),
             ('state', '=', 'current')],
            limit=1,
            order='version DESC')

        return self.merge_xml_builder(current_builder.id)


    # TODO: check whether and which @api decorator is needed here
    def merge_xml_builder(self, builder_id):
        builder_name = self.builder_id.name
        builder = self.browse(builder_id)

        # TODO implement
        return self.xml

    @api.model
    def orbeon_search_read_builder(self, domain=None, fields=None):
        runner = self.search(domain or [], limit=1)
        builder = runner.builder_id

        res = {'id': builder['id']}

        if 'xml' in fields:
            res['xml'] = builder.xml

        return res

    @api.model
    def orbeon_search_read_data(self, domain=None, fields=None):
        runner = self.search(domain or [], limit=1)

        res = {'id': runner['id']}

        if 'xml' in fields:
            if runner.xml is None or runner.xml is False:
                # TODO
                # preprend the <xml> tag from elsewhere? Via builder-API to get right version?
                # code: runner.builder_id.get_xml_form_node(with_xml_tag)
                res['xml'] = '<?xml version="1.0" encoding="utf-8"?>%s' % \
                             runner.builder_id.get_xml_form_node()[0]
                
            else:
                res['xml'] = runner.xml
                
        return res
