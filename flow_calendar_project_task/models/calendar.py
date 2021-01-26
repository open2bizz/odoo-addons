# Copyright Nova Code (http://www.novacode.nl)
# See LICENSE file for full licensing details.

from datetime import datetime
from html2text import html2text

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError

TASK_EVENT_PREFIX = 'P'


class Meeting(models.Model):

    _inherit = "calendar.event"

    flowcal_task_project_id = fields.Many2one(
        'project.project', string='Task Project',
        ondelete='cascade', related='flowcal_task_id.project_id')
    flowcal_task_id = fields.Many2one(
        'project.task', domain="[('project_id', '=', flowcal_task_project_id)]",
        ondelete='cascade', index=True, string='Task')
    flowcal_task_date_deadline = fields.Date(string='Task Deadline', digits=(16,2), related='flowcal_task_id.date_deadline', readonly=True)
    flowcal_task_stage_id = fields.Many2one('project.task.type', related='flowcal_task_id.stage_id', readonly=True, string='Task Stage')

    @api.model
    def default_get(self, flds):
        res = super(Meeting, self).default_get(flds)

        if self._context.get('flowcal_task_id', False):
            task = self.env['project.task'].browse(self._context.get('flowcal_task_id', False))
            res['name'] = self._task_event_name(task)

        return res

    @api.constrains('user_id')
    def _check_user_id_is_task_owner(self):
        self.ensure_one()
        if self.flowcal_task_id and self.flowcal_task_id.user_id and self.flowcal_task_id.user_id != self.user_id:
            raise ValidationError(
                _("Owner of the Calendar Event should be the same user as the assigned Task responsible."))

    @api.onchange('flowcal_task_id')
    def _onchange_task_id(self):
        if self._context.get('default_flow_calendar_model', False) == 'project.task' \
           and not self.id:

            if self.flowcal_task_id:
                self.name = self._task_event_name(self.flowcal_task_id)

                self.user_id = self.flowcal_task_id.user_id
                self.partner_ids = self.flowcal_task_id.user_id.partner_id
            else:
                self.name = '%s: %s' % (TASK_EVENT_PREFIX, _('New'))

    def _task_event_name(self, task):
        if hasattr(task, 'sale_line_id') and task.sale_line_id:
            return "%s: %s" % (task.sale_line_id.order_id.name, task.name)
        else:
            return "%s/%s: %s" % (TASK_EVENT_PREFIX, task.project_id.id, task.name)

    @api.model
    def create(self, vals):
        if not vals.get('flowcal_task_id', False):
            return super(Meeting, self).create(vals)

        task = self.env['project.task'].browse(vals.get('flowcal_task_id'))

        # Set Event its user_id (responsible) and partners/attendees to Task user.
        if task.user_id:
            vals['user_id'] = task.user_id.id
            vals['partner_ids'] = [(4, task.user_id.partner_id.id, False)]

        if vals.get('description', False) and task.description:
            vals['description'] += "\r\n%s" % html2text(task.description)
        elif task.description:
            vals['description'] = html2text(task.description)

        result = super(Meeting, self).create(vals)
        result.write({'res_model': 'project.task', 'res_id': task.id})
        return result

    def action_flow_calendar_event_from_project_task(self):
        form_view = self.env.ref("calendar.view_calendar_event_form")

        return {
            "name": self.name,
            "type": "ir.actions.act_window",
            "res_model": "calendar.event",
            "res_id": self.id,
            "view_mode": "form",
            "views": [
                [form_view.id, "form"],
            ],
            "target": "current",
        }
