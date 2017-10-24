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

    _name = "orbeon.project.runner.stage"
    _description = "Orbeon Project Runner Stage"
    _order = 'sequence, id'

    def _get_mail_template_id_domain(self):
        return [('model', '=', 'orbeon.runner')]

    def _get_default_project_ids(self):
        default_project_id = self.env.context.get('default_project_id')
        return [default_project_id] if default_project_id else None

    name = fields.Char('Stage Name', translate=True, required=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(help="Used to order the Form stages", default=1)
    project_ids = fields.Many2many(
        'project.project', 'orbeon_project_runner_stage_rel', 'orbeon_project_runner_stage_id', 'project_id', string='Projects',
        default=_get_default_project_ids
    )
    legend_blocked = fields.Char(
        string='Kanban Blocked Explanation', translate=True,
        help='Override the default value displayed for the blocked state for kanban selection, when the form is in that stage.')
    legend_done = fields.Char(
        string='Kanban Valid Explanation', translate=True,
        help='Override the default value displayed for the done state for kanban selection, when the form is in that stage.')
    legend_normal = fields.Char(
        string='Kanban Ongoing Explanation', translate=True,
        help='Override the default value displayed for the normal state for kanban selection, when the form is in that stage.')
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

    orbeon_project_runner_stage_ids = fields.Many2many(
        'orbeon.project.runner.stage', 'orbeon_project_runner_stage_rel', 'project_id', 'orbeon_project_runner_stage_id', string='Form Stages'
    )

    @api.one
    def _get_orbeon_runner_forms_count(self):
        self.orbeon_runner_forms_count = self.env["orbeon.runner"].search_count([
            ("res_id", "=", self.id),
            ("res_model", "=", 'project.project'),
        ])

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
        kanban_view = self.env["ir.ui.view"].search([("name", "=", "orbeon.runner_form.kanban")])[0]
        tree_view = self.env["ir.ui.view"].search([("name", "=", "orbeon.runner_form.tree")])[0]
        form_view = self.env["ir.ui.view"].search([("name", "=", "orbeon.runner_form.form")])[0]

        runner_form_ids = [runner_form.id for runner_form in self.orbeon_runner_form_ids]

        if not context.get('default_project_id'):
            context['default_project_id'] = self.id

        return {
            "name": _("Forms"),
            "type": "ir.actions.act_window",
            "res_model": "orbeon.runner",
            "view_type": "kanban",
            "view_mode": "kanban, form, tree",
            "views": [
                [kanban_view.id, "kanban"],
                [form_view.id, "form"],
                [tree_view.id, "tree"]
            ],
            "target": "current",
            "default_project_id": self.id,
            "context": context,
            "domain": [("id", "in", runner_form_ids)],
        }
        
    @api.multi
    def map_orbeon_forms(self, new_project_id):
        forms = self.env['orbeon.runner']
        for form in self.orbeon_runner_form_ids:
            defaults = {}
            if self.state == 'template':
                defaults.update({ 'is_merged' : False
                                , 'stage_id' : form.stage_id.id if form.stage_id else False })
                if form.builder_id.current_builder_id:
                    defaults.update({'builder_id' : form.builder_id.current_builder_id.id})
                new_form = form.copy(defaults)
            else:
                new_stage = False
                for st in self.orbeon_project_runner_stage_ids:
                    if st.sequence == 1:
                        new_stage = st.id
                defaults.update({ 'is_merged' : False
                                , 'stage_id' : new_stage})
                new_form = form.copy(defaults)
                new_form.with_context(lang='nl_NL').merge_current_builder()
            forms += new_form
        return self.browse(new_project_id).write({'orbeon_runner_form_ids': [(6, 0, forms.ids)]})

    @api.multi
    def copy(self, default=None):
        project = super(Project, self).copy(default) 
        self.map_orbeon_forms(project.id)
        return project        
