# -*- encoding: utf-8 -*-
##############################################################################
#
#    open2bizz
#    Copyright (C) 2014 open2bizz (open2bizz.nl).
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
from odoo import fields, models, api

import logging

_logger = logging.getLogger(__name__)

class RunnerFormCopyWizard(models.TransientModel):
    _name = 'wizard.runner.form.copy'
    _description = 'Copy previously added forms'

    target_form_id = fields.Many2one('orbeon.runner', string="Target Form")
    origin_form_id = fields.Many2one('orbeon.runner', string="Origin Form", readonly=True)
    project_id = fields.Many2one('project.project', string="Project", readonly=True)
    patient_id = fields.Many2one('res.partner', string="Patient", readonly=True)
    founder_id = fields.Many2one('orbeon.builder', string="Origin Founder", readonly=True)

    @api.multi
    def copy_runner_form_xml(self):
        for record in self.env['orbeon.runner'].browse(self._context.get('active_ids', [])):
            record.xml = self.target_form_id.xml
            record.copy()
        return True