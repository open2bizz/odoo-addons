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
from odoo import api, fields, models, SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)


class OrbeonRunner(models.Model):
    _inherit = "orbeon.runner"
    _order = "sequence, id"

    @api.model
    def _get_default_stage_id(self):
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False)])

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    project_id = fields.Many2one(
        'project.project',
        compute='_compute_project_id',
        string='Project',
        readonly=True,
        store=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        related='project_id.partner_id',
        string='Partner',
        readonly=True,
        store=True
    )
    user_id = fields.Many2one('res.users', string='Assigned to', index=True, track_visibility='onchange', default=lambda self: self.env.uid)
    user_email = fields.Char(related='user_id.email', string='User Email', readonly=True)
    sequence = fields.Integer(
        string='Sequence', index=True, default=10,
        help="Gives the sequence order when displaying a list of forms."
    )
    stage_id = fields.Many2one(
        'orbeon.project.runner.stage', string='Stage', track_visibility='onchange', index=True,
        domain="[('project_ids', '=', project_id)]", copy=False,
        group_expand='_read_group_stage_ids',
        default=_get_default_stage_id
    )
    kanban_state = fields.Selection([
            ('normal', 'In Progress'),
            ('done', 'Ready for next stage'),
            ('blocked', 'Blocked')
        ], string='Kanban State',
        default='normal',
        track_visibility='onchange',
        required=True, copy=False,
        help="A forms's kanban state indicates special situations affecting it:\n"
             " * Normal is the default situation\n"
             " * Blocked indicates something is preventing the progress of this form\n"
             " * Ready for next stage indicates the form is ready to be pulled to the next stage")
    date_assign = fields.Datetime(string='Assigning Date', index=True, copy=False, readonly=True)
    date_last_stage_update = fields.Datetime(
        string='Last Stage Update',
        default=fields.Datetime.now,
        index=True,
        copy=False,
        readonly=True
    )
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True)

    @api.one
    @api.depends('res_model', 'res_id')
    def _compute_project_id(self):
        if self.res_model == 'project.project':
            project = self.env['project.project'].search([('id', '=', self.res_id)])
            self.project_id = project.id

    @api.onchange('project_id')
    def _onchange_project(self):
        if self.project_id:
            self.stage_id = self.stage_find(self.project_id.id, [('fold', '=', False)])
        else:
            self.stage_id = False

    # ----------------------------------------
    # Stage management
    # ----------------------------------------

    def stage_find(self, project_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all project_ids
        project_ids = []
        if project_id:
            project_ids.append(project_id)
        project_ids.extend(self.mapped('project_id').ids)
        search_domain = []
        if project_ids:
            search_domain = [('|')] * (len(project_ids) - 1)
            for project_id in project_ids:
                search_domain.append(('project_ids', '=', project_id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['orbeon.project.runner.stage'].search(search_domain, order=order, limit=1).id

    @api.model
    def create(self, vals):
        # context: no_log, because subtype already handle this
        context = dict(self.env.context, mail_create_nolog=True)

        # for default stage
        if vals.get('project_id') and not context.get('default_project_id'):
            context['default_res_id'] = vals.get('project_id')
        else:
            vals['res_id'] = context.get('default_project_id', False)
        # user_id change: update date_assign
        if vals.get('user_id'):
            vals['date_assign'] = fields.Datetime.now()
        runner = super(OrbeonRunner, self.with_context(context)).create(vals)
        return runner

    @api.multi
    def write(self, vals):
        now = fields.Datetime.now()
        # stage change: update date_last_stage_update
        if 'stage_id' in vals:
            vals['date_last_stage_update'] = now
            # reset kanban state when changing stage
            if 'project_kanban_state' not in vals:
                vals['kanban_state'] = 'normal'
        # user_id change: update date_assign
        if vals.get('user_id'):
            vals['date_assign'] = now

        result = super(OrbeonRunner, self).write(vals)

        return result

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    @api.multi
    def _track_template(self, tracking):
        res = super(OrbeonRunner, self)._track_template(tracking)
        test_runner = self[0]
        changes, tracking_value_ids = tracking[test_runner.id]
        if 'stage_id' in changes and test_runner.stage_id.mail_template_id:
            res['stage_id'] = (test_runner.stage_id.mail_template_id, {'composition_mode': 'mass_mail'})
        return res

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'kanban_state' in init_values and self.kanban_state == 'blocked':
            return 'orbeon_project.mt_orbeon_project_runner_blocked'
        elif 'kanban_state' in init_values and self.kanban_state == 'done':
            return 'orbeon_project.mt_orbeon_project_runner_ready'
        elif 'user_id' in init_values and self.user_id:  # assigned -> new
            return 'orbeon_project.mt_orbeon_project_runner_new'
        elif 'pstage_id' in init_values and self.stage_id and self.stage_id.sequence <= 1:  # start stage -> new
            return 'orbeon_project.mt_orbeon_project_runner_new'
        elif 'stage_id' in init_values:
            return 'orbeon_project.mt_orbeon_project_runner_stage'
        return super(OrbeonRunner, self)._track_subtype(init_values)
