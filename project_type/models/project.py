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
from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)


class Project(models.Model):
    _inherit = "project.project"

    type_id = fields.Many2one(
        "project.type",
        "Type",
        required=False
    )

    type_name = fields.Char(
        compute='_type_name',
        string='Type'
    )

    is_type_readonly = fields.Boolean(
        "is_type_readonly",
        compute="_is_type_readonly"
    )

    @api.onchange("type_id")
    def _onchange_set_project_name(self):
        if self.partner_id:
            partner_id = self.partner_id.id
        elif 'default_partner_id' in self._context:
            partner_id = self._context['default_partner_id']
        else:
            partner_id = None

        if self.type_id.id:
            counter = self.search_count([
                ('type_id', '=', self.type_id.id),
                ('partner_id', '=', partner_id)]) + 1
            self.name = "%s (%i)" % (self.type_id.name, counter)

    @api.one
    def _is_type_readonly(self):
        self.is_type_readonly = not isinstance(self.id, models.NewId)

    @api.one
    def _type_name(self):
        self.type_name = self.type_id.name
