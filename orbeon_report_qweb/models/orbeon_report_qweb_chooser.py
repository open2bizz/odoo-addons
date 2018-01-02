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
from odoo import fields, models, _, api, osv
from openerp.exceptions import Warning


import logging

_logger = logging.getLogger(__name__)


class OrbeonReportQwebChooser(models.TransientModel):
    _name = 'orbeon.report.qweb.chooser'
    _description = "Choose QWEB report"

    report_xml_id = fields.Many2one(
        'ir.actions.report.xml',
        string="Reports"
    )  
    
    def run_report(self, context={}):
        rep = self.env['orbeon.runner'].browse(context.get('orbeon_runner_id'))
        return rep[0].run_qweb_report(self.report_xml_id.id)
        
    
