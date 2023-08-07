# Copyright 2013-2022 Open2Bizz <info@open2bizz.nl>
# License LGPL-3

from odoo import api, fields, models

class MailActivity(models.Model):
    _inherit = "mail.activity"

    ticket_id = fields.Many2one('helpdesk.ticket', string='Ticket')
    customer_id = fields.Many2one('res.partner', string='Klant')
    project_id = fields.Many2one('project.project', string='Project')

    @api.model
    def create(self, values):
        if self.env['ir.model'].browse(values.get('res_model_id')).model == 'helpdesk.ticket':
            ticket = self.env['helpdesk.ticket'].browse(values.get('res_id'))
            values.update({'project_id':ticket.project_id.id or False,'ticket_id':ticket.id,'customer_id':ticket.partner_id.id})
        return super(MailActivity, self).create(values)
