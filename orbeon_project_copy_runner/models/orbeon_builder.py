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
from odoo import models, fields, api, _

class OrbeonBuilderCopyAction(models.Model):
    _inherit = 'orbeon.builder'

    founder_id = fields.Many2one(
        "orbeon.builder",
        "Builder Founder",
        copy=True,
        readonly=True,
        help="This builder form highest parent_id"
        )

    # This will add the founder_id to any newly made builder forms !!
    @api.model
    def create(self, vals, context=None):
        res = super(OrbeonBuilderCopyAction, self).create(vals)
        if res.version == 1:
            res.write({'founder_id': res.id})
        return res
