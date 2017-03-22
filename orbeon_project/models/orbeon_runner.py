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
from odoo import fields, models


class OrbeonRunner(models.Model):
    _inherit = "orbeon.runner"

    project_id = fields.Many2one(
        "project.project"
    )

# class OrbeonBuilder(models.Model):
#     _inherit = "orbeon.builder"

#     # TODO update project-type linked builder-forms (state=current,obsolete
#     @api.multi
#     def write(self, vals):
#         if 'state' in vals and vals['state'] == 'current':
#             project_type = self.env["project.type"]
