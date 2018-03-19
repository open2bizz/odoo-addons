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

from odoo import fields, models, api, _
from odoo.osv import osv
from odoo.exceptions import UserError, ValidationError

class OrbeonRunnerCopyAction(models.Model):
    _inherit = 'orbeon.runner'

    founder_id = fields.Many2one(
        "orbeon.builder",
        "Builder Founder",
        readonly=True,
        related="builder_id.founder_id"
        )

    @api.multi
    def wizard_copy_form(self):
        if self.xml == False:
            return{
                    'name': _('Copy Runner Form'),
                    'type': 'ir.actions.act_window',
                    'res_model': 'wizard.runner.form.copy',
                    #'view_id': 'runner_form_copy_wizard',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'target': 'new',
                    'context': {'default_patient_id': self.project_id.partner_id.id,'default_target_form_id': self.id, 'default_project_id': self.project_id.id, 'default_founder_id': self.builder_id.founder_id.id},
            }
        else:
             raise UserError(_('Cannot copy a runner form, because this form already contains XML data. Empty the XML field in order to copy a runner form.'))
