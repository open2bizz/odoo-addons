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


class OrbeonRunner(models.Model):
    _inherit = ['orbeon.runner']
    
    builder_reports_count = fields.Integer(
        compute='_builder_reports_count',
        string='Builder reports count'
    )

    @api.one
    def _builder_reports_count(self):
        self.builder_reports_count = len(self.builder_id.report_xml_ids)

    def run_qweb_report(self, report_id):
        rep = self.env['ir.actions.report.xml'].browse(report_id)
        data = {
            'ids': [self.id],
            'model': 'orbeon.runner',
            'form': [self.id],
            'context':{}
        }      
        return {
            'type' : 'ir.actions.report.xml',
            'report_name' : rep.report_name,
            'datas' : data,
            }
        
        

    @api.multi
    def report_button(self, context=None):
        if self.builder_id.report_xml_ids:
            if len(self.builder_id.report_xml_ids) > 1:
                ids = [rec.ir_actions_report_xml_id.id for rec in self.builder_id.report_xml_ids ]
                context.update({ 'rep_ids' : ids, 'orbeon_runner_id' : self.id })
                return {
                        'name': 'Choose report',
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'orbeon.report.qweb.chooser',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        'context': context
                        }
            else:
                return self.run_qweb_report(self.builder_id.report_xml_ids[0].ir_actions_report_xml_id.id )
                
                        

