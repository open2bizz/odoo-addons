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
from odoo import api, fields, models, _
import logging

_logger = logging.getLogger(__name__)


class OrbeonRunnerStage(models.Model):

    _name = "orbeon.runner.stage"
    _description = "Orbeon Runner Stage"
    _order = 'sequence, id'

    def _get_mail_template_id_domain(self):
        return [('model', '=', 'orbeon.runner')]

    def _get_default_project_ids(self):
        default_project_id = self.env.context.get('default_project_id')
        return [default_project_id] if default_project_id else None

    name = fields.Char('Stage Name', translate=True, required=True)
    sequence = fields.Integer(help="Used to order the Form stages", default=1)
    project_ids = fields.Many2many(
        'project.project', 'project_orbeon_runner_stage_rel', 'orbeon_runner_stage_id', 'project_id', string='Projects',
        default=_get_default_project_ids
    )
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=lambda self: self._get_mail_template_id_domain(),
        help="If set an email will be sent to the customer when the form reaches this step."
    )
    fold = fields.Boolean('Folded by Default')


class Project(models.Model):
    _inherit = "project.project"

    orbeon_runner_form_ids = fields.One2many(
        "orbeon.runner",
        "res_id",
        domain=[('res_model', '=', 'project.project')],
        string="Orbeon Runner Forms",
    )

    orbeon_runner_forms_count = fields.Integer(
        "Number of Orbeon Runner Forms",
        compute="_get_orbeon_runner_forms_count",
    )

    orbeon_runner_stage_ids = fields.Many2many(
        'orbeon.runner.stage', 'project_orbeon_runner_stage_rel', 'project_id', 'orbeon_runner_stage_id', string='Form Stages'
    )

    @api.one
    def _get_orbeon_runner_forms_count(self):
        self.orbeon_runner_forms_count = self.env["orbeon.runner"].search_count([
            ("res_id", "=", self.id),
            ("res_model", "=", 'project.project'),
        ])

    @api.model
    def create(self, vals):
        res = super(Project, self).create(vals)
        runner = self.env["orbeon.runner"]

        for builder in res.type_id.orbeon_builder_form_ids:
            runner.create({
                'builder_id': builder.id,
                'name': builder.name,
                'res_id': res.id,
            })

        return res

    @api.multi
    def write(self, vals):
        res = super(Project, self).write(vals)
        if 'active' in vals:
            # archiving/unarchiving a project does it on its forms, too
            forms = self.with_context(active_test=False).mapped('orbeon_runner_form_ids')
            forms.write({'active': vals['active']})
        return res

    @api.multi
    def action_orbeon_runner_forms(self, context=None, *args, **kwargs):
        tree_view = self.env["ir.ui.view"].search([("name", "=", "orbeon.runner_form.tree")])[0]

        kanban_view = self.env["ir.ui.view"].search([("name", "=", "orbeon.runner_form.kanban")])[0]

        runner_form_ids = [runner_form.id for runner_form in self.orbeon_runner_form_ids]

        if not context.get('default_project_id'):
            context['default_project_id'] = self.id

        # if not context.get('default_project_id'):
        #     context['default_orbeon_runner_stage_id'] = self.form_type_ids

        return {
            "name": _("Forms"),
            "type": "ir.actions.act_window",
            "res_model": "orbeon.runner",
            "view_type": "kanban",
            "view_mode": "kanban, tree",
            "views": [
                [kanban_view.id, "kanban"],
                [tree_view.id, "tree"],
            ],
            "target": "current",
            "default_project_id": self.id,
            "context": context,
            "domain": [("id", "in", runner_form_ids)],
        }
