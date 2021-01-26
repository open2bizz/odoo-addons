# Copyright Nova Code (http://www.novacode.nl)
# See LICENSE file for full licensing details.

from datetime import datetime, date, time

from odoo import api, fields, models


class Meeting(models.Model):

    _inherit = "calendar.event"

    @api.model
    def _set_flow_calendar_model(self):
        return self._context.get('flow_calendar_model', False)

    @api.model
    def _default_start(self):
        return datetime.combine(date.today(), time(11,00,00))

    @api.model
    def _default_stop(self):
        return datetime.combine(date.today(), time(12,00,00))

    flow_calendar_model = fields.Char(
        'Flow Calendar Model Name',
        default=_set_flow_calendar_model
    )

    flow_calendar_model_id = fields.Many2one(
        'ir.model', compute='_compute_flow_calendar_model_id',
        string='Flow Calendar Model'
    )

    start = fields.Datetime(default=_default_start)
    stop = fields.Datetime(default=_default_stop)

    @api.depends('flow_calendar_model')
    def _compute_flow_calendar_model_id(self):
        self.flow_calendar_model_id = self.env['ir.model'].search(
            [('model', '=', self.flow_calendar_model)], limit=1)
