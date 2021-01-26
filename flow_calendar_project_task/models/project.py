# Copyright Nova Code (http://www.novacode.nl)
# See LICENSE file for full licensing details.

from datetime import date, datetime, timedelta

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError, ValidationError


def datetime_gte_today(check_datetime):
    today = date.today()
    check_datetime = fields.Date.to_date(check_datetime)
    return check_datetime >= today


class Task(models.Model):

    _inherit = "project.task"

    flowcal_event_ids = fields.One2many(
        'calendar.event',
        'flowcal_task_id',
        context={'flow_calendar_model': 'project.task'},
        string='Calendar')
    flowcal_event_count = fields.Integer(compute='_compute_flowcal_event_count', string="Calendar Events", default=0)
    flowcal_upcoming_event_start_date = fields.Datetime(compute='_compute_flowcal_upcoming_event_start_date', string='Upcoming Calendar Start')
    flowcal_upcoming_event_count = fields.Integer(compute='_compute_flowcal_event_count', string="Calendar Events", default=0)

    @api.constrains('date_deadline', 'flowcal_event_ids')
    def _check_date_deadline(self):
        if not self.date_deadline:
            return

        # TODO Odoo-12 read as native Python datetime objects
        date_deadline = fields.Date.from_string(self.date_deadline)

        for event in self.flowcal_event_ids:
            if event.allday:
                stop_date = fields.Date.from_string(event.stop_date)
            else:
                stop_date = fields.Datetime.from_string(event.stop_datetime).date()

            if stop_date > date_deadline:
                raise ValidationError(
                _("A Calendar Event after Deadline isn't allowed."))

    @api.depends('flowcal_event_ids')
    def _compute_flowcal_event_count(self):
        for task in self:
            task.flowcal_event_count = len(task.flowcal_event_ids)
            task.flowcal_upcoming_event_count = len([e.start for e in task.flowcal_event_ids if datetime_gte_today(e.start)])

    def _compute_flowcal_upcoming_event_start_date(self):
        for task in self:
            if task.flowcal_event_ids:
                upcoming = [fields.Datetime.to_datetime(e.start) for e in task.flowcal_event_ids if datetime_gte_today(e.start)]
                if upcoming:
                    task.flowcal_upcoming_event_start_date = min(upcoming)
                else:
                    task.flowcal_upcoming_event_start_date = False
            else:
                task.flowcal_upcoming_event_start_date = False

    def write(self, vals):
        """If changed task-user:
        - Remove task-user its partner from event partner_ids (attendees).
        - Add new task-user its partner to event partner_ids (attendees).
        """
        results = []
        new_user_id = vals.get('user_id', False)

        if new_user_id:
            new_user = self.env['res.users'].browse(new_user_id)

        for task in self:
            origin_user = task.user_id

            if new_user_id and task.flowcal_event_ids:
                for event in task.flowcal_event_ids:
                    event.user_id = new_user_id
                    event.partner_ids = [(4, new_user.partner_id.id, False)]

                    partner_ids = event.partner_ids.mapped('id')
                    if origin_user.partner_id.id in partner_ids:
                        event.partner_ids = [(3, origin_user.partner_id.id, False)]

            res = super(Task, task).write(vals)
            results.append(res)

        return (False not in results)

    def action_flow_calendar_event_load_project_task(self):
        """Open a window to plan Task in Calendar, with the
        flowcal_task_project_id and flowcal_issue_id loaded in context.
        """
        self.ensure_one()
        ctx = dict(self.env.context or {})
        return {
            'name': _('Meetings'),
            'type': 'ir.actions.act_window',
            'view_type': 'calendar',
            'view_mode': 'calendar,tree,form',
            'res_model': 'calendar.event',
            'context': ctx,
        }

    def delete_upcoming_calendar_event(self):
        self.ensure_one()
        [e.unlink() for e in self.flowcal_event_ids if datetime_gte_today(e.start)]
