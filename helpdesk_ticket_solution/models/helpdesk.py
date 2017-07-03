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

from odoo import api, fields, models, _
from odoo.exceptions import  ValidationError
import logging
_logger = logging.getLogger(__name__)

class HelpdeskTicket(models.Model):
    _inherit = 'helpdesk.ticket'
    
    solution = fields.Html(
        string = 'Solution'
    )
    default_solution = fields.Many2one(
        comodel_name = 'default.data',
        string = 'Default Solution',
        domain = "[('model', '=', 'helpdesk.ticket'), ('field', '=', 'solution')]"
    )
    
    @api.onchange("default_solution")
    def onchange_default_solution(self):
        if self.default_solution:
            update_data = self.default_solution.get_update_default_data(self.solution)
            if update_data['update']:
                self.solution = update_data['data']
